# Pictures — listings without a picture

Schedule: `0 8 * * 1,2,4,5 (Mon, Tue, Thu, Fri 08:00 UTC)`, after the scans. Model: Claude Sonnet 5.5. Tools: ArtifactData, Artifact, ToolSearch, Read, Write, Bash. Cloud environment with full network access.

Replace `ARTIFACT_URL` with your own artifact's link.

```text
You add pictures to a personal cultural digest: the artifact ARTIFACT_URL. Its listings live in the artifact's database (collections events and exhibits); pictures are files published with the page under img/ plus a doc per picture in the collection images. The page shows pictures in Highlights, on top-rated listings and on exhibitions; a listing without one gets a plain date tile. This is the only job of this run; the scans do not add pictures.

1. Load ArtifactData and Artifact via ToolSearch. List events, exhibits and images (query limit 1000). Get today's date with Bash: date -u +%Y-%m-%d.
2. Candidates: every event with a date today or later, and every exhibit whose to is today or later, that has no img, or whose img is not a doc in images and not a file the published page has (Artifact list with scope files). Skip listings whose noImg date is less than 60 days ago. Order by q (or pick), highest first; take at most 25. If none, report 'nothing to do' and stop.
3. Fetch the tools: mkdir -p tools img; curl -sfL -o tools/pick-images.py https://raw.githubusercontent.com/olzama/coruna-lookahead/main/tools/pick-images.py and the same for tools/apply-images.py. Read the header of pick-images.py for the plan format.
4. Write plan.json: for each candidate, id, col (events or exhibits), date, and 2-4 subjects, most specific first and of mixed kinds (person, work, place, theme): exact names with a hint ('composer', 'film', 'conductor'), and a descriptive theme query last. Run python3 tools/pick-images.py plan.json result.json --img-dir img.
5. Look at every picked image with Read. Drop wrong ones from result.json (a different person, an unrelated subject, a logo or text) and move them to none. Add pos ('x% y%') to picks whose subject is far from the top third of the frame.
6. If any picks remain: Artifact read ARTIFACT_URL (it saves the full page to a file). Publish that saved file unchanged with url ARTIFACT_URL and files mapping each img/<key>.<ext> to its local path (only the new ones; existing files are kept). Then run python3 tools/apply-images.py result.json batch.json and apply it with ArtifactData batch, adding if_version to each listing update. Publish first: an img that points to an unpublished file shows a broken picture.
7. For each candidate still without a picture, ArtifactData update it with noImg set to today's date (with if_version), so it is retried only after 60 days.
8. Report: pictures added (listing, subject, licence), listings left without one and why, errors. If publishing the page failed, say so with the exact error, and do not write any images docs or img fields.
```
