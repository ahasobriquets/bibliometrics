####Evolocumab-FDA-NDA-Medical.txt
As of July 30, 2015, evolocumab (Repatha) has not been approved by FDA, but there are plenty of references to work with in the clicinal trials and the FDA Briefing Document:
* https://clinicaltrials.gov/ct2/results?term=evolocumab&Search=Search
* http://www.fda.gov/downloads/AdvisoryCommittees/CommitteesMeetingMaterials/Drugs/EndocrinologicandMetabolicDrugsAdvisoryCommittee/UCM450072.pdf

####Evolocumab-core.pklz
```
python src/topdown.py --format cse --levels 2 input/Evolocumab-FDA-NDA-Medical.txt output/Evolocumab-core.pklz
```
Ran o/n.

####Evolocumab-core-scored-*.pklz
```
python src/score.py --article-scoring propagate --neighbor-scoring indegree output/Evolocumab-core.pklz output/Evolocumab-core-scored-indegree.pklz
python src/score.py --article-scoring propagate --neighbor-scoring sum output/Evolocumab-core.pklz output/Evolocumab-core-scored-sum.pklz
```

####Evolocumab-core-scored-*.xgmml
```
python src/xgmml.py output/Evolocumab-core-scored-indegree.pklz output/Evolocumab-core-scored-indegree.xgmml
python src/xgmml.py output/Evolocumab-core-scored-sum.pklz output/Evolocumab-core-scored-sum.xgmml
```
Network properties:
* 1548 articles (1950-2015)
* 7350 authors
* 4846 institutions
* 37 grant agencies
* 26 clinical trials 


####Evolocumab-Pubmed-Search-PMIDs*.txt
For the peripheral network, we will try sampling from the following search term:
* (("1900/1/1"[Date - Publication] : "2015/03/11"[Date - Publication])) AND ldl cholesterol reduction
 * 9593 hits spanning 1971-2015 
  * took 200 pmids from every 6th page to collect 1600 pubs, 5 
   * 1,7,13,...43 | 2,8,14,...44 | 3,9,15,...45 | 4,10,16,..46 | 5,11,17,..47

##Evo5ocumab-peripheral.pklz
Note: only level 1 if providing comparable number of pmids from pubmed search, i.e., comparable to core network article count.
```
python src/topdown.py --format pmid --dont-search-trials --levels 1 input/Evolocumab-Pubmed-Search-PMIDs.txt output/Evolocumab-peripheral.pklz
```
Ran in 30 sec or 30min (noticed big difference for two different lists of 1600 pmids; not sure why)

####Evolocumab-peripheral-individual-indegree*.pklz
```
python src/score.py --article-scoring individual --neighbor-scoring indegree output/Evolocumab-peripheral.pklz output/Evolocumab-peripheral-individual-indegree1.pklz
python src/score.py --article-scoring individual --neighbor-scoring indegree output/Evolocumab-peripheral.pklz output/Evolocumab-peripheral-individual-indegree2.pklz
python src/score.py --article-scoring individual --neighbor-scoring indegree output/Evolocumab-peripheral.pklz output/Evolocumab-peripheral-individual-indegree3.pklz
python src/score.py --article-scoring individual --neighbor-scoring indegree output/Evolocumab-peripheral.pklz output/Evolocumab-peripheral-individual-indegree4.pklz
python src/score.py --article-scoring individual --neighbor-scoring indegree output/Evolocumab-peripheral.pklz output/Evolocumab-peripheral-individual-indegree5.pklz
```

####Evolocumab-peripheral-scored-*.xgmml
```
python src/xgmml.py output/Evolocumab-peripheral-individual-indegree1.pklz output/Evolocumab-peripheral-individual-indegree1.xgmml
python src/xgmml.py output/Evolocumab-peripheral-individual-indegree2.pklz output/Evolocumab-peripheral-individual-indegree2.xgmml
python src/xgmml.py output/Evolocumab-peripheral-individual-indegree3.pklz output/Evolocumab-peripheral-individual-indegree3.xgmml
python src/xgmml.py output/Evolocumab-peripheral-individual-indegree4.pklz output/Evolocumab-peripheral-individual-indegree4.xgmml
python src/xgmml.py output/Evolocumab-peripheral-individual-indegree5.pklz output/Evolocumab-peripheral-individual-indegree5.xgmml
```
Network properties (average):
* 1598 articles (1992-2015); 1548 articles (1987-2014)
* 7656 authors; 7452 authors
* 4622 institutions; 4165 institutions
* 23 grantagencies; 37 grantagencies

####Analysis
* Opened scored xgmml in Cytoscape
* Selected authors into new subnetwork; selected institutes into new subnetwork
* Exported default node tables for each subnetwork
* Opened csv in excel
* Pasted authors and scores from core-scored-sum author subnetworks into CP-Prop columns in analysis.xlsx template
* Pasted authors and ct_scores from core-scored-sum author subnetworks into CT-Count columns
* Pasted authors and score from core-scored-indegree author subnetworks into CP-Indegree columns
* Pasted authors and score from peripheral-scored-indegree author subnetwork into Denom-Indegree columns
* Pasted authors and score from peripheral-scored-indegree2 author subnetwork into Denom-Indegree2 columns
* Template formulas calculation ranks and ratios
* Note: averaged ratios across two samples of peripheral (see Evolocumab-Pubmed-Search-PMIDs*.txt above) to get a better RBR filter criteria, i.e., it covers more of the pubmed search result space, without compromizing the scope and size contraints of a given peripheral network. Two samples of 1600 each (3200) from a total space of 9722 is sufficient. Future analyses might sample more if covering more space.

CPI subnetwork:
* 342 articles (1974-2014)
* 27 authors
* 7 institutes (4 unique)