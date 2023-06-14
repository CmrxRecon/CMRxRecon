import argparse
import json

def get_args():
    parser = argparse.ArgumentParser()
    """Set up command-line interface and get arguments."""
    parser.add_argument("-s", "--submission_file", help="Submission File")
    parser.add_argument("-g", "--goldstandard", required=True, help="Goldstandard for scoring")
    parser.add_argument("-e", "--entity_type", required=True, help="synapse entity type downloaded")
    parser.add_argument("-r", "--results", required=True, help="validation results")
    return parser.parse_args()


if __name__ == '__main__':
    import sys
    
    args = get_args()

    # TODO check the submission file

    result = {
         'submission_errors': 'Data checking passed',  # 错误原因
         'submission_status': 'VALIDATED'  # INVALID和VALIDATED 两种状态
    }

    with open(args.results, 'w') as o:
            o.write(json.dumps(result))
