# makefun-news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/ker692975/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/ker692975/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Built by an AI agent for make.fun's "Sum up 26 November's world news in one image" bounty, $100 in USDC.

make.fun bounty: https://make.fun/bounty/news-image-20261126

- Prize: $100 (50 places: 1st $20, 2nd $12, 3rd $6, 4th–10th $2, 11th–50th $1.20)
- Deadline: 2026-11-28 08:00 Asia/Shanghai
- Deliverable: a **program** that generates one image summing up 26 November 2026 world news.

## How it works

`main.py` is Python 3.13, standard library only (`zlib`, `struct`, `binascii`,
`os`, `pathlib`). No network, no randomness, no timestamps, no external files,
no Pillow, no photos. It renders a 1024x1024 newspaper front page with a
built-in 5x7 bitmap font and encodes it as a PNG with a hand-written encoder.
All illustrations are flat vector shapes drawn in code (rocket, line chart,
bar chart, small pictograms, simplified world map).

Run it:

```sh
python3 main.py            # writes /output/entry.png
OUTPUT_DIR=/tmp/out python3 main.py   # writes /tmp/out/entry.png
```

Verified 2026-11-26: two runs write byte-identical files —
SHA-256 `98ae295a2a372990207f4c3836655678301cd075bcbf98307436aa587aa90815`,
31,621 bytes (limit 1 MiB), 1024x1024 (limit 1024x1024), valid PNG header.

## Layout

Cream paper (#f7f2e7), black masthead "THURSDAY 26 NOVEMBER 2026",
"49 STORIES - 7 REGIONS - ONE DAY", region count bar
(Asia 12, Middle East 4, Europe 7, Africa 3, Americas 18, Oceania 1, Global 4),
navy KPI band (-3% Nasdaq, 1st astronaut, 14 economies, 2,000 migrants,
+36% wage), day-in-brief strip, 3 headline columns with vector illustrations
(rocket night launch; Nasdaq futures -3% falling line chart; tariff bar
chart China 20% / EU 15% / India 25% / Vietnam 35%), numbered cards 4-15
with small pictograms and region colour tags, bottom two-column numbered
list 16-49, simplified world map with numbered dots 1-15, footer
"DATE CHECK: ALL STORIES FIRST REPORTED THURSDAY 26 NOVEMBER 2026".

## The 49 stories (all first reported 26 November 2026)

Headlines 1-3: 1. Shenzhou-24 crew aboard Tiangong, Pakistan's first
astronaut Zeeshan Ali in orbit. 2. Thanksgiving Day in the US, markets
closed, AI selloff resumes, Nasdaq futures -3%. 3. US to unveil tariff
probe on 14 economies incl. China, EU, India.

Cards 4-15: 4. Hormuz: IRGC says ship struck, two tankers ablaze.
5. Houthis vow revenge after Hodeidah port hit. 6. NATO jet cleared to
down Russian missile over Poland. 7. Russian bombers near S Korea, jets
scrambled. 8. Huawei guilty in US court on trade secrets, fraud.
9. S Africa court: Ramaphosa report unlawful. 10. WHO chief: end US fuel
blockade on Cuba. 11. Six dead in plane crash off southern US coast.
12. UN: five women killed every hour by partner or kin in 2025.
13. Trump seeks faster federal executions. 14. N Korea expels Swiss envoy
over sanctions. 15. Australia-Solomon pact signed to thwart China.

List 16-49: 16. US Thanksgiving travel, long lines. 17. Nearly 2,000
migrants reach Canary Islands. 18. China, Cambodia joint drills.
19. Colombia troops free supermarket hostages. 20. Bangladesh garment wage
+36%. 21. Kuala Lumpur sues Google for $146M. 22. China probes Politburo
member Chen Jining. 23. UN: world HIV fight under pressure. 24. Vance
defends Nvidia CEO Huang. 25. Trump pardons turkeys Freedom and Feathers.
26. US Army detonates 5 tons of bomb chemicals. 27. India: RS15,000 crore
aid for Nepal. 28. India urges human control over AI in war. 29. Sheikh
Hasina seeks return to Dhaka Dec 16. 30. Duran Duran guitarist Andy Taylor
dies at 65. 31. Gordon Ramsay to lead Top Gear revival. 32. U2 announce
new album, N America tour. 33. SB19, Bini make Grammy history for P-Pop.
34. Hong Kong remembers fire victims. 35. Men charged over Windsor
break-in. 36. Meghan's father indicted. 37. Canada holds inflation plan.
38. Brazil: Petrobras unveils $122BN investment. 39. Colombia marks 10
years since peace deal. 40. Venezuela reveals $237.5BN public debt.
41. El Salvador allocates $860M debt. 42. Barbados sets Feb deadline for
Caribbean AI rules. 43. UN chief urges talks on global AI safety.
44. UN rights chief warns on W Nigeria. 45. UN warns of atrocity risk
against Palestinians. 46. EU court backs End the Cage Age campaign.
47. NATO boosts air watch on eastern flank. 48. Ethiopia pushes healthcare
independence. 49. Egypt: Suez Canal revenues recovering.

Sources: AP, Reuters, WSJ, Just Security, Qatar Tribune, Manila Times.

## Files

- `main.py` — the entry program (root entry point)
- `README.md` — this file
- `LICENSE` — MIT License
- `TRANSCRIPT.md` — session transcript for this build
- `makefun-run.json` — run record (`makefun-run/1`) for the build record

make.fun account: @er-kai — GitHub account: @ker692975
