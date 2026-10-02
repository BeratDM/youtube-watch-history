import json
from collections import Counter
import pandas as pd
from lxml import etree
import argparse
import os
from time import perf_counter


def read_file_with_progress(file_path):
    total_size = os.path.getsize(file_path)
    bytes_read = 0
    last_reported_percentage = 0
    content = bytearray()

    print("Reading input:   0%", end="", flush=True)
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            content.extend(chunk)
            bytes_read += len(chunk)
            percentage = min(100, int(bytes_read * 100 / total_size)) if total_size else 100
            if percentage >= last_reported_percentage + 1 and percentage < 100:
                print(f"\rReading input: {percentage:3d}%", end="", flush=True)
                last_reported_percentage = percentage

    print("\rReading input: 100%")
    return content.decode("utf-8")


def load_json(file_path):
    try:
        data = json.loads(read_file_with_progress(file_path))
        return Counter(
            f"{entry['title'].replace('Watched ', '')} - {entry['subtitles'][0]['name'].replace(' - Topic', '') if 'subtitles' in entry else 'Unknown Artist'}"
            for entry in data
            if "header" in entry and entry["header"] == "YouTube Music"
        )
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return Counter()


def load_html(file_path):
    try:
        song_counts = Counter()
        outer_classes = {
            "outer-cell",
            "mdl-cell",
            "mdl-cell--12-col",
            "mdl-shadow--2dp",
        }
        header_classes = {"header-cell", "mdl-cell", "mdl-cell--12-col"}
        content_classes = {
            "content-cell",
            "mdl-cell",
            "mdl-cell--6-col",
            "mdl-typography--body-1",
        }
        total_size = os.path.getsize(file_path)
        bytes_read = 0
        processed_cards = 0
        last_reported_percentage = 0
        parser = etree.HTMLPullParser(events=("end",), encoding="utf-8")

        def process_available_events():
            nonlocal processed_cards
            for _, cell in parser.read_events():
                classes = set((cell.get("class") or "").split())
                if cell.tag != "div" or not outer_classes.issubset(classes):
                    continue

                processed_cards += 1
                header = next(
                    (
                        element
                        for element in cell.iter("div")
                        if header_classes.issubset(
                            set((element.get("class") or "").split())
                        )
                    ),
                    None,
                )
                content = next(
                    (
                        element
                        for element in cell.iter("div")
                        if content_classes.issubset(
                            set((element.get("class") or "").split())
                        )
                    ),
                    None,
                )

                if (
                    header is not None
                    and "YouTube Music" in "".join(header.itertext())
                    and content is not None
                ):
                    links = list(content.iter("a"))
                    if len(links) > 1:
                        song_title = "".join(links[0].itertext())
                        artist = "".join(links[1].itertext()).replace(
                            " - Topic", ""
                        )
                        song_counts[f"{song_title} - {artist}"] += 1

                cell.clear(keep_tail=True)
                parent = cell.getparent()
                if parent is not None:
                    while cell.getprevious() is not None:
                        del parent[0]

        print("Parsing history:   0% (0 cards)", end="", flush=True)
        with open(file_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                bytes_read += len(chunk)
                parser.feed(chunk)
                process_available_events()

                percentage = (
                    min(100, int(bytes_read * 100 / total_size)) if total_size else 100
                )
                if percentage > last_reported_percentage and percentage < 100:
                    print(
                        f"\rParsing history: {percentage:3d}% ({processed_cards:,} cards)",
                        end="",
                        flush=True,
                    )
                    last_reported_percentage = percentage

        parser.close()
        process_available_events()
        print(f"\rParsing history: 100% ({processed_cards:,} cards)")

        return song_counts
    except Exception as e:
        print(f"Error loading HTML file: {e}")
        return Counter()


def export_top_songs(df, amount, export_format):
    output_file = f"top_{amount}_songs.{export_format}"
    try:
        if export_format == "txt":
            with open(output_file, "w", encoding="utf-8") as f:
                for index, row in df.iterrows():
                    title, artist = row["Song"].rsplit(" - ", 1)
                    f.write(f"{index + 1}: {title} - {artist}. {row['Plays']} plays\n")
        elif export_format == "json":
            json_data = [
                {
                    "index": index + 1,
                    "Title": row["Song"].rsplit(" - ", 1)[0],
                    "Artist": row["Song"].rsplit(" - ", 1)[1],
                    "Plays": row["Plays"],
                }
                for index, row in df.iterrows()
            ]
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        elif export_format == "csv":
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("Count,Title,Artist,Plays\n")
                for index, row in df.iterrows():
                    title, artist = row["Song"].rsplit(" - ", 1)
                    f.write(f"{index + 1},{title},{artist},{row['Plays']}\n")
        print(
            f"Top {amount} most listened-to songs have been exported to {output_file}."
        )
    except Exception as e:
        print(f"Error exporting top songs: {e}")


def figure_top_songs(df):
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Use seaborn color palette
    colors = sns.color_palette("viridis", len(df.head(10)))

    df_top_10 = df.head(10)
    df_top_10.plot(kind="barh", x="Song", y="Plays", legend=False, color=colors)
    plt.title(f"Top 10 Most Played Songs", fontsize=14)
    plt.xlabel("Number of Plays", fontsize=12)
    plt.ylabel("Song", fontsize=12)
    plt.gca().invert_yaxis()
    plt.tight_layout()

    # Set the window title
    manager = plt.get_current_fig_manager()
    manager.set_window_title("Top 10 Most Played Songs")

    # Save the figure as a PNG file
    plt.savefig("top_10_songs.png", bbox_inches="tight")
    print("The graph have been saved as top_10_songs.png.")

    plt.show()


def determine_file_type(file_path):
    json_file = f"{file_path}.json"
    html_file = f"{file_path}.html"

    if file_path.endswith(".json"):
        return "json", file_path
    elif file_path.endswith(".html"):
        return "html", file_path
    elif os.path.exists(json_file):
        return "json", json_file
    elif os.path.exists(html_file):
        return "html", html_file
    else:
        print("No valid input file found. Please provide a valid JSON or HTML file.")
        return None, None


def main():
    parser = argparse.ArgumentParser(description="Process YouTube Music history.")
    parser.add_argument(
        "--file_path",
        type=str,
        default="watch-history",
        help="Path to the input file without extension",
    )
    parser.add_argument(
        "--export_format",
        type=str,
        choices=["txt", "json", "csv"],
        default="txt",
        help="Export format for the top songs",
    )
    parser.add_argument(
        "--amount", type=int, default=10, help="Number of top songs to export"
    )
    parser.add_argument(
        "--figure", action="store_true", help="Figure the top 10 most played songs"
    )

    args = parser.parse_args()

    file_type, file_path_with_extension = determine_file_type(args.file_path)
    if not file_type:
        return

    if file_type == "json":
        song_counts = load_json(file_path_with_extension)
    elif file_type == "html":
        song_counts = load_html(file_path_with_extension)

    if not song_counts:
        print("No song titles found. Please check the input file.")
        return

    top_songs = song_counts.most_common(args.amount)

    df = pd.DataFrame(top_songs, columns=["Song", "Plays"])

    export_top_songs(df, args.amount, args.export_format)

    if args.figure:
        try:
            figure_top_songs(df)
        except ImportError:
            print(
                "matplotlib and seaborn are not installed. Please install them to use the figuring feature."
            )
            print(
                "You can install them using the command: pip install matplotlib seaborn"
            )


if __name__ == "__main__":
    start_time = perf_counter()
    try:
        main()
    finally:
        elapsed_time = perf_counter() - start_time
        print(f"Total execution time: {elapsed_time:.2f} seconds")
