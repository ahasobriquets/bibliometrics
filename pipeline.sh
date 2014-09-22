basename="${1}"
input_format="${2}"
num_levels="${3}"

dont_search_trials=""
if [ "${input_format}" = "pmid" ]; then
  dont_search_trials="--dont-search-trials"
fi

output_dir="${basename}-${num_levels}-levels-output"

mkdir "${output_dir}"
python src/topdown.py "--format=${input_format}" "--levels=${num_levels}" "${dont_search_trials}" "input/${basename}.txt" "${output_dir}/net"
python src/xgmml.py "${output_dir}/net.pkl.gz" "${output_dir}/${basename}"
tar pczf "${output_dir}/${basename}.xgmml.tar.gz" "${output_dir}/${basename}.xgmml"
for t in author institution grantagency; do
  python src/degreesort.py "${output_dir}/net.pkl.gz" "${t}" "${output_dir}/${basename}-${t}"
done


