# Sources folder

`download_sources.py` downloads the public Scento CC BY 4.0 dataset and FragDB's public sample. Put any separately licensed FragDB full bundle in `sources/fragdb/` using the same file names to merge it locally or in a private CI workflow. Put JSON/JSONL exports produced by fragscrape in `sources/fragscrape/`.

Do not publish FragDB full files unless your license permits redistribution. fragscrape is code, not a static database; scraped records remain subject to the source sites' terms and need review.
