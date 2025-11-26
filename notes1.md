# x

<https://www.reddit.com/r/YoutubeMusic/comments/uc0y57/is_there_a_way_to_view_most_played_songs/>

<https://gist.github.com/biast12/dafc5d6e33612953e3e4da2ea54cd305>

## Top YouTube Music Songs Processor

This Python script processes your YouTube Music watch history (extracted via Google Takeout) to generate a list of your most-played songs. It supports both `.json` and `.html` files and includes options to export the top songs in multiple formats (txt, json, csv) and visualize the top 10 most played songs.

## Features

- **Supports JSON and HTML files**: Automatically detects whether the input file is in JSON or HTML format.
- **Counts song plays**: Extracts song titles and the number of times they were played.
- **Exports top songs**: Saves the list of top songs to a `.txt`, `.json`, or `.csv` file.
- **Optional data visualization**: Generates a bar chart of the top 10 songs using `matplotlib` and `seaborn`.

## Script Options

All flags are optional

- `--file_path`: Path to the input file. Default is `watch-history` within the same folder.
- `--amount`: Number of top songs to export. Default is 10.
- `--export_format`: Format for exporting the top songs. Available options: `txt`, `json`, `csv`. Default is `txt`.
- `--figure`: Generates a bar chart showing the top 10 most played songs and saves an image of it.

## How to Use

### 1. Export Data from Google Takeout

- Go to [Google Takeout](https://takeout.google.com/).
- Select only **YouTube and YouTube Music** data.
- **For faster processing**, choose JSON format when downloading the data.
- Extract the `watch-history.json` or `watch-history.html` file from the downloaded archive.

### 2. Install Dependencies

The script requires the following Python libraries:

```bash
pip install beautifulsoup4 pandas matplotlib seaborn
```

### 3. Run the Script

You can run the script without any flags, and it will use the default options:

```bash
python top_youtube_music_songs.py
```

To customize the behavior, use the available flags:

```bash
python top_youtube_music_songs.py --file_path "/path/to/your/watch-history" --amount 100 --export_format json --figure
```

- Replace `/path/to/your/watch-history` with the actual path to your JSON or HTML file.
- Use `--amount` to specify the number of top songs to export.
- Use `--export_format` to choose the export format (`txt`, `json`, `csv`).
- Add the `--figure` flag to visualize the top 10 songs as a bar chart and save it as a `.png` file.

### Example

```bash
python top_youtube_music_songs.py --file_path "watch-history" --amount 50 --export_format json
```

This will export the top 50 most played songs to a `top_50_songs.json` file.

### 4. Output

- A `.txt`, `.json`, or `.csv` file containing your most-played songs.
- (Optional) A bar chart showing the top 10 most played songs saved as a `.png` file.

### working - python 1/top_youtube_music_songs.py --file_path "watch-history" --amount 100 --export_format txt
