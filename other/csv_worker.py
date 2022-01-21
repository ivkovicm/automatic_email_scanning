import csv
from other import custom_errors


def string_to_csv(report: str) -> str:
    try:
        with io.StringIO() as output:
            csv_writer = csv.writer(output)
            csv_writer.writerows(report)
            report_out = output.read()
    except:
        logging.error("Error while converting report to csv!")
        raise custom_errors.ConvertToCSVError

    return report_out
