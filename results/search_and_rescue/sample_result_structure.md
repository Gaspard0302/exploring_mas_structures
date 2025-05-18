# Sample Result Structure for Search and Rescue

This directory will contain results from the Search and Rescue simulation runs.

## Expected Files

For each run, the system will generate:

1. `result_[timestamp].txt` - Contains the final result text including:
   - Summary of survivors found
   - Locations and conditions
   - Rescue priorities
   - Execution time

2. `memory_log_[timestamp].json` - Contains the detailed execution log:
   - All agent communications
   - Decision points
   - Context updates
   - Performance metrics

## Example File Naming

- `result_20230415_143022.txt`
- `memory_log_20230415_143022.json`

## Analysis

The results can be analyzed to measure:
- Task completion efficiency
- Accuracy of survivor detection
- Quality of rescue prioritization
- Information sharing effectiveness
- Adaptability to changing conditions 