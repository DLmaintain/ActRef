# Baselines
Please refer to the baselines' repository or follow the instruction bellow
## PyRef
https://github.com/PyRef/PyRef

## MLRefScanner
https://github.com/seal-replication-packages/TOSEM2024
_Notice: The MLRefScanner needs a business tool "Understand" for code metrics analysis, please refer to the Homepage(https://scitools.com/)_

## LLMs
Use run_LLM.py
export OPENAI_API_KEY=your_key_here

python run_LLM_baseline.py \
    --commit_dir commits \
    --prompt ..\doc\Prompt \
    --output_dir outputs

## Evaluation
Please run the cal_pr_TOOLNAME.py to calculate the metrics value, use the data.csv as ground truth
