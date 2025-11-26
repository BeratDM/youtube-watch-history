import json
from collections import Counter
import pandas as pd
from bs4 import BeautifulSoup
import argparse
import os


def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        song_titles = [
            f"{entry['title'].replace('Watched ', '')} - {entry['subtitles'][0]['name'].replace(' - Topic', '') if 'subtitles' in entry else 'Unknown Artist'}"
            for entry in data
            if "header" in entry and entry["header"] == "YouTube Music"
        ]
        return song_titles
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []


def load_html(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")

        song_titles = []
        outer_cells = soup.find_all(
            "div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"
        )

        for cell in outer_cells:
            header = cell.find("div", class_="header-cell mdl-cell mdl-cell--12-col")
            if header and "YouTube Music" in header.get_text():
                content_cells = cell.find_all(
                    "div",
                    class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1",
                )
                if len(content_cells) > 0:
                    song_title_element = content_cells[0].find("a")
                    artist_elements = content_cells[0].find_all("a")
                    if song_title_element and len(artist_elements) > 1:
                        song_title = song_title_element.get_text()
                        artist = artist_elements[1].get_text().replace(" - Topic", "")
                        song_titles.append(f"{song_title} - {artist}")

        return song_titles
    except Exception as e:
        print(f"Error loading HTML file: {e}")
        return []


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
        song_titles = load_json(file_path_with_extension)
    elif file_type == "html":
        song_titles = load_html(file_path_with_extension)

    if not song_titles:
        print("No song titles found. Please check the input file.")
        return

    song_counts = Counter(song_titles)
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
    main()
