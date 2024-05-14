import { promises as fs } from "fs";
import rssParser from "rss-parser";

const DEFAULT_N = 5;

type Entry = {
  title?: string;
  link?: string;
  isoDate?: string;
};

const fetchFeed = async (url: string): Promise<string[]> => {
  try {
    const parser = new rssParser();
    const response = await parser.parseURL(url);
    let feeds = [];

    for (const item of response.items) {
      if (item.title && item.link) feeds.push(formatFeedEntry(item));
      if (feeds.length === DEFAULT_N) break;
    }

    return feeds;
  } catch (error) {
    console.error("Error fetching or parsing the feed:", error);
    return [];
  }
};

const formatFeedEntry = ({ title, link, isoDate }: Entry): string => {
  const date = isoDate ? new Date(isoDate).toISOString().slice(0, 10) : "";
  return date ? `[${title}](${link}) - ${date}` : `[${title}](${link})`;
};

const replaceChunk = (
  content: string,
  marker: string,
  chunk: string,
  inline: boolean = false
): string => {
  const startMarker = `<!-- ${marker} start -->`;
  const endMarker = `<!-- ${marker} end -->`;

  const pattern = new RegExp(`${startMarker}[\\s\\S]*${endMarker}`, "g");

  if (!inline) {
    chunk = `\n${chunk}\n`;
  }

  return content.replace(pattern, `${startMarker}${chunk}${endMarker}`);
};

const updateReadme = async (): Promise<void> => {
  const url = "https://tduyng.github.io/atom.xml";
  const feeds = await fetchFeed(url);

  try {
    const readmePath = `${process.cwd()}/README.md`;
    let readmeContent = await fs.readFile(readmePath, "utf-8");
    readmeContent = replaceChunk(readmeContent, "blog", feeds.join("\n\n"));
    await fs.writeFile(readmePath, readmeContent, "utf-8");
    console.log("README.md updated successfully!");
  } catch (error) {
    console.error("Error updating README.md:", error);
  }
};

await updateReadme();
