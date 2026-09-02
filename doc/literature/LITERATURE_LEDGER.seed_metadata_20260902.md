# Literature Ledger

This is an evidence ledger, not a bibliography. No record has been added to
the manuscript or to the BibTeX database.

## Verification convention

- **DISCOVERED:** candidate only.
- **METADATA_VERIFIED:** title, authors, venue, year, and DOI checked against
  a publisher, proceedings, institutional, author, or DBLP record.
- **PDF_VERIFIED:** primary paper checked for the relevant claim.
- **FULLY_READ:** read sufficiently for detailed novelty comparison.

Descriptions in a metadata-only record are limited to the verified abstract or
record summary. Strong novelty comparisons require PDF_VERIFIED or FULLY_READ.
A dash in PDF/local path means that no local copy has been retained in
literature/papers.

## Seed corpus

### bourgault2003coordinated

- **Exact title:** Coordinated Decentralized Search for a Lost Target in a Bayesian World
- **Exact authors:** Frédéric Bourgault; Tomonari Furukawa; Hugh F. Durrant-Whyte
- **Venue / year / DOI:** Proceedings 2003 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS 2003), 2003, pp. 48--53; DOI 10.1109/IROS.2003.1250604.
- **Peer-reviewed status / PDF/local path:** IEEE IROS conference paper; — (public author-hosted PDF located).
- **Verification source:** [IEEE Xplore](https://doi.org/10.1109/IROS.2003.1250604); [author PDF](https://cornell-asl.org/wiki/images/7/76/Bourgault03coord.pdf).
- **Research theme / problem / core method:** Bayesian multi-platform lost-target search; decentralized coordination of autonomous sensors for one non-evading target; Bayesian decentralized data fusion and planning.
- **Experimental setting:** Simulated airborne vehicles; stationary and drifting targets lost at sea.
- **Direct relevance / difference:** Foundational probabilistic multi-vehicle target search; it has no human intervention, future human prediction, or fixed responsibility anchor.
- **Potential novelty threat:** low.
- **Safe claims:** Decentralized Bayesian coordination of multiple autonomous platforms searching for a single non-evading target, with stationary and drifting lost-at-sea simulations.
- **Do not attribute:** Human--robot collaboration or predictive spatial responsibility redistribution.
- **Verification status:** METADATA_VERIFIED; open PDF should be read locally.

### heintzman2021anticipatory

- **Exact title:** Anticipatory Planning and Dynamic Lost Person Models for Human-Robot Search and Rescue
- **Exact authors:** Larkin Heintzman; Amanda Hashimoto; Nicole Abaid; Ryan K. Williams
- **Venue / year / DOI:** 2021 IEEE International Conference on Robotics and Automation (ICRA), 2021, pp. 8252--8258; DOI 10.1109/ICRA48506.2021.9562070.
- **Peer-reviewed status / PDF/local path:** IEEE ICRA conference paper; — (public NSF PDF located).
- **Verification source:** [NSF public-access PDF](https://par.nsf.gov/servlets/purl/10302700); [DOI record](https://doi.org/10.1109/ICRA48506.2021.9562070).
- **Research theme / problem / core method:** Anticipatory SAR planning; UAV assistance that accounts for lost-person motion, anticipated human-searcher trajectories, and fixed-FOV sensing; integrated posterior-risk planning.
- **Experimental setting:** Monte Carlo UAV SAR simulations.
- **Direct relevance / difference:** Closest seed paper on anticipated human-searcher trajectories; it models a dynamic lost person, not a human-controlled USV reserved as a fixed spatial anchor.
- **Potential novelty threat:** high.
- **Safe claims:** It incorporates a lost-person model, anticipated human-searcher trajectories, fixed-FOV sensing, and posterior-risk planning in SAR simulation.
- **Do not attribute:** The paper's exact responsibility partition, fixed-anchor re-clustering, or H2/H3/H4 design.
- **Verification status:** METADATA_VERIFIED; PDF verification is required before novelty prose.

### swamy2020scaled

- **Exact title:** Scaled Autonomy: Enabling Human Operators to Control Robot Fleets
- **Exact authors:** Gokul Swamy; Siddharth Reddy; Sergey Levine; Anca D. Dragan
- **Venue / year / DOI:** 2020 IEEE International Conference on Robotics and Automation (ICRA), 2020, pp. 5942--5948; DOI 10.1109/ICRA40945.2020.9196792.
- **Peer-reviewed status / PDF/local path:** IEEE ICRA conference paper; — (open version located).
- **Verification source:** [CMU record](https://publications.ri.cmu.edu/scaled-autonomy-enabling-human-operators-to-control-robot-fleets); [arXiv](https://arxiv.org/abs/1910.02910).
- **Research theme / problem / core method:** Scalable fleet supervision; selecting which robot a single operator should teleoperate; learned operator-selection preferences.
- **Experimental setting:** Simulated navigation, 12-participant user study, and hardware mobile robot.
- **Direct relevance / difference:** Supports one-operator fleet supervision; does not predict the spatial responsibility of an already controlled robot for search reallocation.
- **Potential novelty threat:** medium.
- **Safe claims:** A single operator can supervise a fleet and teleoperate one robot at a time; operator robot-selection preferences are modeled.
- **Do not attribute:** Maritime probabilistic search, target-belief updates, or fixed-anchor redistribution.
- **Verification status:** METADATA_VERIFIED; open PDF should be read locally.

### lippi2023task

- **Exact title:** A Task Allocation Framework for Human Multi-Robot Collaborative Settings
- **Exact authors:** Martina Lippi; Paolo Di Lillo; Alessandro Marino
- **Venue / year / DOI:** 2023 IEEE International Conference on Robotics and Automation (ICRA), 2023, pp. 7614--7620; DOI 10.1109/ICRA48891.2023.10161458.
- **Peer-reviewed status / PDF/local path:** IEEE ICRA conference paper; — (arXiv version located).
- **Verification source:** [DBLP](https://dblp.org/rec/conf/icra/LippiLM23); [arXiv](https://arxiv.org/abs/2210.14036).
- **Research theme / problem / core method:** Human--multi-robot task allocation; allocation and reallocation in production; offline allocation plus online reallocation considering plan inaccuracies, events, human preferences, and switching costs.
- **Experimental setting:** Two manipulators with a human in box filling.
- **Direct relevance / difference:** Establishes online human--multi-robot reallocation; it is not probabilistic free-cell search responsibility.
- **Potential novelty threat:** medium.
- **Safe claims:** It combines offline allocation with online reallocation in a human--multi-robot setting.
- **Do not attribute:** Maritime search, Bayesian target belief, or anticipated human spatial responsibility.
- **Verification status:** METADATA_VERIFIED; open PDF should be read locally.

### wu2021spatial

- **Exact title:** Spatial Intention Maps for Multi-Agent Mobile Manipulation
- **Exact authors:** Jimmy Wu; Xingyuan Sun; Andy Zeng; Shuran Song; Szymon Rusinkiewicz; Thomas A. Funkhouser
- **Venue / year / DOI:** 2021 IEEE International Conference on Robotics and Automation (ICRA), 2021, pp. 8749--8756; DOI 10.1109/ICRA48506.2021.9561359.
- **Peer-reviewed status / PDF/local path:** IEEE ICRA conference paper; — (author project PDF located).
- **Verification source:** [DBLP](https://dblp.org/rec/conf/icra/WuSZSRF21); [project page](https://spatial-intention-maps.cs.princeton.edu/).
- **Research theme / problem / core method:** Spatial intention representations for decentralized mobile manipulation; communicating intention among agents; map-aligned representations for multi-agent deep reinforcement learning.
- **Experimental setting:** Simulated heterogeneous mobile-manipulation tasks.
- **Direct relevance / difference:** A conceptual neighbor for spatial intent; no human intervention, Bayesian target search, or center-induced responsibility allocation.
- **Potential novelty threat:** medium.
- **Safe claims:** It proposes spatial intention maps for improving coordination in multi-agent mobile manipulation.
- **Do not attribute:** Human intent, USVs, or fixed responsibility anchors.
- **Verification status:** METADATA_VERIFIED; open PDF should be read locally.

### best2015bayesian

- **Exact title:** Bayesian Intention Inference for Trajectory Prediction with an Unknown Goal Destination
- **Exact authors:** Graeme Best; Robert Fitch
- **Venue / year / DOI:** 2015 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2015; DOI 10.1109/IROS.2015.7354203.
- **Peer-reviewed status / PDF/local path:** IEEE IROS conference paper; —; NEEDS_CAMPUS_PDF if no author copy is obtained.
- **Verification source:** [IROS 2015 digest](https://www.iros2015.org/docs/IROS_Digest_WWW.pdf); [DOI record](https://doi.org/10.1109/IROS.2015.7354203).
- **Research theme / problem / core method:** Bayesian intention inference; unknown-goal and future-trajectory prediction for a mobile agent in clutter; multi-modal goal hypotheses with Monte Carlo trajectory prediction.
- **Experimental setting:** Pedestrian datasets.
- **Direct relevance / difference:** Delimits future-motion prediction from this paper's planning-level use of a prediction; no fleet search allocation or human-controlled USVs.
- **Potential novelty threat:** medium.
- **Safe claims:** Bayesian inference of intended goal and future trajectory of a mobile agent in clutter, evaluated on pedestrian data.
- **Do not attribute:** Human--multi-USV planning, target belief, or responsibility redistribution.
- **Verification status:** METADATA_VERIFIED; primary PDF required for detailed comparison.

### javdani2015shared

- **Exact title:** Shared Autonomy via Hindsight Optimization
- **Exact authors:** Shervin Javdani; Siddhartha S. Srinivasa; J. Andrew Bagnell
- **Venue / year / DOI:** Robotics: Science and Systems XI (RSS), 2015; DOI 10.15607/RSS.2015.XI.032.
- **Peer-reviewed status / PDF/local path:** RSS conference paper; — (open version located).
- **Verification source:** [RSS/DBLP](https://dblp.org/rec/conf/rss/JavdaniSB15); [arXiv](https://arxiv.org/abs/1503.07619).
- **Research theme / problem / core method:** Shared autonomy under uncertain user goals; assistance for a user with unknown goal; POMDP, maximum-entropy inverse optimal control, and hindsight optimization.
- **Experimental setting:** User study against predict-then-blend.
- **Direct relevance / difference:** Background for user-intent inference and assistance; it assists a controlled task rather than redistributing a remaining fleet's search responsibility.
- **Potential novelty threat:** medium.
- **Safe claims:** It studies shared autonomy with uncertain user goals and evaluates hindsight optimization against predict-then-blend.
- **Do not attribute:** Fleet re-clustering, maritime search, or target posterior updates from human input.
- **Verification status:** METADATA_VERIFIED; open PDF should be read locally.

### li2024multirobot

- **Exact title:** Multi-robot Search in a 3D Environment with Intersection System Constraints
- **Exact authors:** Yan-Shuo Li; Kuo-Shih Tseng
- **Venue / year / DOI:** 2024 IEEE International Conference on Robotics and Automation (ICRA), 2024, pp. 5963--5969; DOI 10.1109/ICRA57147.2024.10610393.
- **Peer-reviewed status / PDF/local path:** IEEE ICRA conference paper; —; NEEDS_CAMPUS_PDF unless an author copy is obtained.
- **Verification source:** [National Central University record](https://scholars.ncu.edu.tw/en/publications/multi-robot-search-in-a-3d-environment-with-intersection-system-c/); [DOI record](https://doi.org/10.1109/ICRA57147.2024.10610393).
- **Research theme / problem / core method:** Multi-robot 3-D search and task allocation; coverage and balancing under routing and clustering constraints; submodular maximization with intersection-system constraints.
- **Experimental setting:** Comparative multi-robot-search experiments; details require the paper.
- **Direct relevance / difference:** Recent ICRA search/allocation comparison; no verified human-in-the-loop, Bayesian target belief, or fixed human anchor.
- **Potential novelty threat:** medium.
- **Safe claims:** It formulates multi-robot search with coverage, balancing, routing, and clustering constraints.
- **Do not attribute:** Unverified sensing details or any human responsibility semantics.
- **Verification status:** METADATA_VERIFIED; prioritize primary PDF access.

### matos2016multiple

- **Exact title:** Multiple Robot Operations for Maritime Search and Rescue in euRathlon 2015 Competition
- **Exact authors:** Aníbal Matos; Alfredo Martins; André Dias; Bruno Ferreira; José Miguel Almeida; Hugo Ferreira; Guilherme Amaral; André Figueiredo; Rui Almeida; Filipe Silva
- **Venue / year / DOI:** OCEANS 2016 MTS/IEEE Shanghai, 2016, pp. 1--7; DOI 10.1109/OCEANSAP.2016.7485707.
- **Peer-reviewed status / PDF/local path:** IEEE OCEANS proceedings; peer-review policy not independently checked; — (repository PDF located).
- **Verification source:** [INESC TEC repository](https://recipp.ipp.pt/entities/publication/57cf2c83-d1a8-4759-ab1d-f68834621574); [repository PDF](https://repositorio.inesctec.pt/bitstream/123456789/3975/1/P-00K-NAF.pdf).
- **Research theme / problem / core method:** Maritime multi-robot SAR; reports euRathlon operations; surface survey supports AUV mission planning.
- **Experimental setting:** ROAZ USV, MARES AUV, and multi-domain robots in euRathlon 2015.
- **Direct relevance / difference:** Maritime SAR application context; not a human--multi-USV probabilistic search formulation.
- **Potential novelty threat:** low.
- **Safe claims:** Surface and underwater robotic operations supported maritime situation assessment, mapping, leak detection, and victim localization.
- **Do not attribute:** Camera-based Bayesian search, future human prediction, or responsibility redistribution.
- **Verification status:** METADATA_VERIFIED; open PDF should be read locally.

### queralta2020collaborative

- **Exact title:** Collaborative Multi-Robot Search and Rescue: Planning, Coordination, Perception, and Active Vision
- **Exact authors:** Jorge Peña Queralta; Jussi Taipalmaa; Bilge Can Pullinen; Victor Kathan Sarker; Tuan Nguyen Gia; Hannu Tenhunen; Moncef Gabbouj; Jenni Raitoharju; Tomi Westerlund
- **Venue / year / DOI:** IEEE Access, vol. 8, 2020, pp. 191617--191643; DOI 10.1109/ACCESS.2020.3030190.
- **Peer-reviewed status / PDF/local path:** Refereed IEEE Access journal article; —.
- **Verification source:** [University of Turku record](https://research.utu.fi/converis/portal/detail/Publication/50080855?lang=en_GB); [DOI record](https://doi.org/10.1109/ACCESS.2020.3030190).
- **Research theme / problem / core method:** Review of collaborative multi-robot SAR; planning, coordination, perception, and active vision; review article rather than one runtime method.
- **Experimental setting:** Not applicable.
- **Direct relevance / difference:** Broad SAR background; it does not establish predictive spatial responsibility redistribution.
- **Potential novelty threat:** low.
- **Safe claims:** Multi-robot systems can support SAR through mapping, situational assessment, monitoring, communication, and victim search.
- **Do not attribute:** A unified experimental algorithm or the proposed mechanism.
- **Verification status:** METADATA_VERIFIED; relevant sections need reading before detailed prose.

## REAL-WORLD MOTIVATION SOURCES

These are background facts, not robotics evidence.

- **MH370 date and persons aboard:** ATSB records the 8 March 2014 disappearance and 239 passengers and crew lost. [ATSB 10th-anniversary statement](https://www.atsb.gov.au/news/2024/atsb-acknowledges-10th-anniversary-mh370-disappearance).
- **ATSB-led underwater search:** ATSB records more than 120,000 km² searched using high-resolution sonar between October 2014 and January 2017. [ATSB statement](https://www.atsb.gov.au/news/2024/atsb-acknowledges-10th-anniversary-mh370-disappearance); [operational report](https://www.atsb.gov.au/sites/default/files/media/5773565/operational-search-for-mh370_final_3oct2017.pdf).
- **Historical total:** ATSB records total seafloor searched close to 200,000 km² after the later Ocean Infinity search. [ATSB overview](https://www.atsb.gov.au/mh370-search-overview).
- **Renewal and extension:** Malaysia's Ministry of Transport records a 25 March 2025 agreement with Ocean Infinity for a new estimated 15,000-km² area. Reuters reported on 29 June 2026 a 12-month extension from 1 July 2026 to 30 June 2027. [Malaysian Ministry of Transport](https://www.mot.gov.my/en/Kenyataan%20Media/Year%202026/MH370%20Search%20Operation%202025-2026%20-%20Update%20to%20Families.pdf); [Reuters](https://www.marketscreener.com/news/malaysia-extends-search-for-missing-flight-mh370-by-one-year-ce7f5fdedc81f12c).
- **Scope limit:** MH370 is background motivation only. This paper's 2-D camera-based multi-USV simulation does not reproduce the deep-ocean MH370 search and must not claim direct applicability without additional evidence.

## Recommended first five PDFs for full reading

1. Heintzman et al. (2021): highest novelty threat and closest anticipatory-search comparison.
2. Bourgault et al. (2003): Bayesian multi-platform target-search foundation.
3. Best and Fitch (2015): future-motion prediction versus planning-level prediction use.
4. Lippi et al. (2023): human--multi-robot online reallocation boundary.
5. Li and Tseng (2024): recent ICRA search/allocation comparison; obtain by campus access if necessary.
