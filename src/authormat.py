import sys
import collections
import pandas
import igraph
import numpy
import scipy.stats
import argparse

def outgoing_counts_of_type(articles, node_type):
  '''Given a list of article nodes, returns a list of the number of neighbors each article
  has that match the given type. E.g., if node_type == "author", this will return a list
  of the number of authors connected to each article node.'''

  return [len([neighbor for neighbor in article.neighbors(mode = igraph.OUT) if neighbor['type'] == node_type]) for article in articles]

def h_index(counts):
  n = len(counts)
  indexed_counts = [0] * (n + 1)
  for i in range(n):
    indexed_counts[min(counts[i], n)] += 1

  running_sum = 0
  for i in range(n, -1, -1):
    running_sum += indexed_counts[i]
    if running_sum >= i:
      return i
  return 0

def tg_score(articles):
  tg_count = 0
  total_count = 0

  visited = set()

  for article in articles:
    for citing_article in filter(lambda n: n['type'] == 'article' and n['pubtypes'] != None, article.neighbors(mode = igraph.OUT)):
      if citing_article.index in visited: continue
      visited.add(citing_article.index)
      total_count += 1
      for pubtype in map(lambda t: t.lower(), citing_article['pubtypes']):
        if not ('trial' in pubtype or 'guideline' in pubtype): continue
        tg_count += 1
        break
  if total_count == 0:
    return 0
  else:
    return tg_count / float(total_count)

def lists_of_co_authors(articles, author_name):
  '''Returns a nested list, where each sublist is a list of co-authors for each article.
  This will filter out all authors who match the given author_name.'''

  # Unfortunately a one-liner for speed reasons
  return [[author['label'] for author in article.neighbors(mode = igraph.OUT) if (author['type'] == 'author' and not author['label'].lower().startswith(author_name))] for article in articles]

def flatten(list_of_lists):
  '''Takes a nested list and returns a single-level list.'''
  return [elem for a_list in list_of_lists for elem in a_list]

def calc_co_author_freqs_and_uniqueness(articles, author_name):
  '''Returns the tuple (dict, float). The first value is a dictionary of co-author frequencies
  across all given articles. The second is the co-author uniqueness. This is the ratio of
  the number of unique co-authors to the total number of co-authors.'''

  co_authors_lists = lists_of_co_authors(articles, author_name)
  all_co_authors = flatten(co_authors_lists)
  if len(all_co_authors) == 0:
    return (None, None)
  co_authors_counts = collections.Counter(all_co_authors)
  num_articles = float(len(co_authors_lists))
  freqs = [count / num_articles for count in co_authors_counts.values()]

  num_unique_authors = len(co_authors_counts)
  uniqueness = num_unique_authors / float(len(all_co_authors))

  return (freqs, uniqueness)

def calc_metrics(graph_file_path, mat):
  '''Calculates the values for each column for the given
  graph_file_path and stores in the in the matrix.'''
  g = igraph.Graph.Read(graph_file_path, format='picklez')
  author_name = g['name'].lower()
  author = g.vs.find(label = author_name, type='author')

  level_1_articles = author.neighbors(mode = igraph.OUT)
  if len(level_1_articles) == 0:
    return

  coauthor_counts = outgoing_counts_of_type(level_1_articles, 'author')
  coauthor_freqs, coauthor_uniqueness = calc_co_author_freqs_and_uniqueness(level_1_articles, author_name)
  institution_counts = outgoing_counts_of_type(level_1_articles, 'institution')
  grantagency_counts = outgoing_counts_of_type(level_1_articles, 'grantagency')
  article_years = [article['pubdate'] / 10000 for article in level_1_articles if article['pubdate'] != None]
  #citcounts = outgoing_counts_of_type(level_1_articles, 'article')
  citcounts = [article['citcount'] for article in level_1_articles if article['citcount'] != None]

  mat.loc[author_name] = float('nan')

  if coauthor_counts:
    mat['mean-co-authors'][author_name] = numpy.mean(coauthor_counts)
    mat['median-co-authors'][author_name] = numpy.median(coauthor_counts)
    mat['sd-co-authors'][author_name] = numpy.std(coauthor_counts)
    mat['skew-co-authors'][author_name] = scipy.stats.skew(coauthor_counts)
    mat['kurt-co-authors'][author_name] = scipy.stats.kurtosis(coauthor_counts)
    mat['num-articles-over-20-coauthors'][author_name] = len([count for count in coauthor_counts if count >= 20])

  if institution_counts:
    mat['mean-institutions'][author_name] = numpy.mean(institution_counts)
    mat['median-institutions'][author_name] = numpy.median(institution_counts)
    mat['sd-institutions'][author_name] = numpy.std(institution_counts)

  if grantagency_counts:
    mat['mean-grant-agencies'][author_name] = numpy.mean(grantagency_counts)
    mat['median-grant-agencies'][author_name] = numpy.median(grantagency_counts)
    mat['sd-grant-agencies'][author_name] = numpy.std(grantagency_counts)

  if article_years:
    mat['delta-pub-years'][author_name] = max(article_years) - min(article_years)
    mat['mean-pub-years'][author_name] = numpy.mean(article_years)
    mat['median-pub-years'][author_name] = numpy.median(article_years)
    mat['sd-pub-years'][author_name] = numpy.std(article_years)
    mat['skew-pub-years'][author_name] = scipy.stats.skew(article_years)
    mat['kurt-pub-years'][author_name] = scipy.stats.kurtosis(article_years)

  if coauthor_freqs:
    mat['mean-collab-freq'][author_name] = numpy.mean(coauthor_freqs)
    mat['median-collab-freq'][author_name] = numpy.median(coauthor_freqs)
    mat['sd-collab-freq'][author_name] = numpy.std(coauthor_freqs)
    mat['collab-uniqueness'][author_name] = coauthor_uniqueness

  if citcounts:
    mat['h-index'][author_name] = h_index(citcounts)
    mat['max-citations'][author_name] = max(citcounts)

  if level_1_articles:
    mat['tg-score'][author_name] = tg_score(level_1_articles)

def write_matrix(graph_file_paths, output_file_path):
  mat = pandas.DataFrame(columns = [
    'mean-co-authors', 'median-co-authors', 'sd-co-authors', 'skew-co-authors', 'kurt-co-authors',
    'num-articles-over-20-coauthors',
    'mean-institutions', 'median-institutions', 'sd-institutions',
    'mean-grant-agencies', 'median-grant-agencies', 'sd-grant-agencies',
    'delta-pub-years', 'mean-pub-years', 'median-pub-years', 'sd-pub-years', 'skew-pub-years', 'kurt-pub-years',
    'mean-collab-freq', 'median-collab-freq', 'sd-collab-freq', 'collab-uniqueness',
    'h-index', 'max-citations', 'tg-score'])
  for graph_file_path in graph_file_paths:
    calc_metrics(graph_file_path, mat)
  mat.to_csv(output_file_path, mode='w')

def calc_coauthor_counts(graph_file_path, output_file):
  g = igraph.Graph.Read(graph_file_path, format='picklez')
  author_name = g['name'].lower()
  author = g.vs.find(label = author_name, type='author')

  level_1_articles = author.neighbors(mode = igraph.OUT)
  coauthor_counts = outgoing_counts_of_type(level_1_articles, 'author')

  output_file.write(author_name)
  output_file.write('\n')
  output_file.write(' '.join(map(str, coauthor_counts)))
  output_file.write('\n')

def write_coauthor_counts(graph_file_paths, output_file_path):
  with open(output_file_path, 'w') as output_file:
    for graph_file_path in graph_file_paths:
      calc_coauthor_counts(graph_file_path, output_file)

def _parse_args(raw_args):
  parser = argparse.ArgumentParser()
  parser.add_argument('--type', choices=['matrix', 'coauthor_counts'], default='matrix')
  parser.add_argument('output')
  parser.add_argument('inputs', nargs='+')
  return parser.parse_args(raw_args)

if __name__ == '__main__':
  args = _parse_args(sys.argv[1:])
  if args.type == 'matrix':
    write_matrix(args.inputs, args.output)
  elif args.type == 'coauthor_counts':
    write_coauthor_counts(args.inputs, args.output)
