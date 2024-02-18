import argparse
import csv
from datetime import datetime
from typing import Dict, List, Tuple


class DataPoint:
    def __init__(self, row: List[str]) -> None:
        if len(row) >= 1:
            try:
                self.dt = datetime.strptime(row[0].strip(), "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"error {e} while parsing {row[0]}")
        if len(row) >= 2:
            self.hr = float(row[1])

    def __str__(self) -> str:
        return f"datetime: {self.dt} hr: {self.hr}"

    def to_dict(self) -> Dict[str, str]:
        return {"dt": self.dt.strftime("%Y-%m-%d %H:%M:%S"), "hr": str(self.hr)}


def get_partition_key(dt: datetime, partition: str):
    if partition == "yearly":
        return str(dt.year)
    if partition == "montly":
        return f"{dt.year}_{dt.month}"
    return "default_key"


def get_breakdown_key(dt: datetime, partition: str):
    if partition == "daily":
        return dt.strftime("%Y-%m-%d")
    if partition == "hourly":
        return dt.strftime("%Y-%m-%d %H:00:00")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_breakdown_datapoints(
    datapoints: List[DataPoint], partition: str, breakdown: str
) -> Dict[str, Dict[str, List[DataPoint]]]:
    breakdown_datapoints = {}
    for datapoint in datapoints:
        if datapoint.dt is not None:
            key = get_partition_key(datapoint.dt, partition)
            breakdown_key = get_breakdown_key(datapoint.dt, breakdown)
            if key not in breakdown_datapoints:
                breakdown_datapoints[key] = {}
            if breakdown_key not in breakdown_datapoints[key]:
                breakdown_datapoints[key][breakdown_key] = []
            breakdown_datapoints[key][breakdown_key].append(datapoint)
    return breakdown_datapoints


def compute_output_dataset_from_breakdown_datapoints(
    breakdown_datapoints: Dict[str, Dict[str, List[DataPoint]]],
) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
    output_dataset = {}
    for parition_key, breakdown_to_datapoints in breakdown_datapoints.items():
        output_list = []
        for breakdown_key, datapoints in breakdown_to_datapoints.items():
            hrs = [int(dp.hr) for dp in datapoints]
            avg_hr = sum(hrs) / len(datapoints)
            max_hr = max(hrs)
            min_hr = min(hrs)
            output_datapoint = {
                "dt": breakdown_key,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "min_hr": min_hr,
            }
            output_list.append((breakdown_key, output_datapoint))
        output_dataset[parition_key] = sorted(output_list)
    return output_dataset


def main(args):
    print(args.file)
    datapoints: List[DataPoint] = []
    with open(args.file) as f:
        result = csv.reader(f, delimiter=",", quotechar='"')
        for i, row in enumerate(result):
            if i != 0:
                datapoints.append(DataPoint(row))
    print(f"data len {len(datapoints)}")
    breakdown_datapoints = get_breakdown_datapoints(
        datapoints, args.partition, args.breakdown
    )
    print(len(breakdown_datapoints))
    output_dataset = compute_output_dataset_from_breakdown_datapoints(
        breakdown_datapoints
    )
    for parition_key, clustered_datapoints in output_dataset.items():
        with open(f"{args.output}/{parition_key}_{args.breakdown}.csv", "w") as f:
            writer = csv.DictWriter(f, ["dt", "avg_hr", "max_hr", "min_hr"])
            writer.writeheader()
            for _, dp in clustered_datapoints:
                writer.writerow(dp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    required_group = parser.add_argument_group("required_args")
    required_group.add_argument("-f", "--file", type=str, required=True)
    required_group.add_argument(
        "-p", "--partition", type=str, choices=["yearly", "monthly"], required=True
    )
    required_group.add_argument(
        "-b",
        "--breakdown",
        type=str,
        choices=["daily", "hourly", "none"],
        required=True,
    )
    required_group.add_argument("-o", "--output", type=str, required=True)
    args = parser.parse_args()
    main(args)
