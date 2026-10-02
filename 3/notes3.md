# How to use

## 1. Export Data from Google Takeout

- Go to [Google Takeout](https://takeout.google.com/).
- Create a request and select only **My Activity** data.
- Edit the **My Activity** content options and select only **Youtube**. Activity Format can be both html or json.
- Extract the `MyActivity` or `watch-history` file with either json or html from the downloaded archive.

## 2. Use the script

- Replace `/path/to/your/watch-history` with the actual path to your JSON or HTML file.
- Use `--amount` to specify the number of top songs to export.
- Use `--export_format` to choose the export format (`txt`, `json`, `csv`).
- Add the `--figure` flag to visualize the top 10 songs as a bar chart and save it as a `.png` file.

## Example

`python 3/top_youtube_music_songs.py --file_path "MyActivity" --amount 200 --export_format txt --figure`
