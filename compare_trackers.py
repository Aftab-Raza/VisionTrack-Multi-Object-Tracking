import csv
from pathlib import Path

import config


def load_summary(
    file_path
):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(
            file
        )

        row = next(
            reader
        )

        return row


def main():

    benchmark_directory = Path(
        config.BENCHMARK_DIRECTORY
    )


    bytetrack_file = (

        benchmark_directory
        /
        "bytetrack_summary.csv"

    )


    custom_file = (

        benchmark_directory
        /
        "custom_summary.csv"

    )


    if not bytetrack_file.exists():

        print(
            "ByteTrack benchmark "
            "not found."
        )

        return


    if not custom_file.exists():

        print(
            "Custom MOT benchmark "
            "not found."
        )

        return


    bytetrack = load_summary(
        bytetrack_file
    )


    custom = load_summary(
        custom_file
    )


    print()

    print(
        "=" * 76
    )

    print(
        "VISIONTRACK TRACKER COMPARISON"
    )

    print(
        "=" * 76
    )


    print(

        f"{'Metric':<28}"
        f"{'ByteTrack':>20}"
        f"{'Custom MOT':>20}"

    )


    print(
        "-" * 76
    )


    metrics = [

        (
            "Total Frames",
            "total_frames"
        ),

        (
            "Average FPS",
            "average_fps"
        ),

        (
            "Tracking Time (ms)",
            "average_tracking_ms"
        ),

        (
            "Frame Latency (ms)",
            "average_processing_ms"
        ),

        (
            "P95 Latency (ms)",
            "p95_processing_ms"
        ),

        (
            "Unique Track IDs",
            "unique_track_ids"
        ),

        (
            "Avg Active Objects",
            "average_active_objects"
        )

    ]


    for label, key in metrics:

        print(

            f"{label:<28}"
            f"{bytetrack[key]:>20}"
            f"{custom[key]:>20}"

        )


    print(
        "=" * 76
    )


if __name__ == "__main__":

    main()