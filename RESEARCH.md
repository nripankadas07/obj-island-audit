# Research — 17 October 2026

User: CAD/export pipeline maintainers inspecting a triangulated OBJ before downstream processing.

Pain: Disconnected parts, seam duplicates and orientation conflicts need attributable face/edge evidence rather than an unexplained pass/fail.

Smallest useful capability: Explain edge-connected triangle islands and edge defects in a bounded OBJ mesh.

Acceptance: Recover two closed islands, attribute boundary/nonmanifold/orientation/contact defects, validate interleaved relative indices and reject forward/zero references and unsupported polygons.

Demand is inferred from the workflow and adjacent public evidence, not a verified request for this product. Discovery path: descriptive GitHub topics, a runnable invented example and the chronological portfolio index. No unsolicited outreach or activity manipulation.

## Current alternatives

Live GitHub repository search, sorted **Most stars**, query `3D data processing` and the related broad queries recorded in [provenance](RESEARCH_PROVENANCE.json). Highest-star relevant comparable found in this inspected scope: **isl-org/Open3D**. This is not an exhaustive global ranking.

| Repository | Stars observed | Last push observed (UTC) | Archived | API license classification |
| --- | ---: | --- | --- | --- |
| [isl-org/Open3D](https://github.com/isl-org/Open3D) | 14098 | 2026-09-30T10:06:02Z | False | NOASSERTION |
| [cnr-isti-vclab/meshlab](https://github.com/cnr-isti-vclab/meshlab) | 5870 | 2026-08-25T20:38:52Z | False | GPL-3.0 |
| [mikedh/trimesh](https://github.com/mikedh/trimesh) | 3702 | 2026-10-14T19:23:27Z | False | MIT |

Open3D already clusters connected triangles and computes manifold evidence. Trimesh already offers adjacency, splitting and watertightness operations; MeshLab offers a broad interactive processing workflow. Trimesh PR 2620 discusses interleaved OBJ relative indices. Our explicit small-file evidence report is a narrower interface, not an absent competitor feature.

Open3D or Trimesh scripts, or interactive MeshLab filters.

Current README, selected source semantics and up to five issue/PR records were read. Exact observation times, source blob identities, queries and public issue URLs are in provenance. API NOASSERTION means unclassified license, not permission to copy. No third-party implementation or fixtures are bundled.

Our small Python wheel installs with one command after checkout and includes a direct example. Established alternatives have broader APIs, formats, documentation, examples and support communities. Competitor installations, time to first useful result, reliability, support response and performance were not measured. Our example only proves our documented behavior. Stars inform discovery, not quality or performance.

Portfolio distinction: No existing owned repository is a triangle OBJ topology inspector. Point-table, GIS and media index tools do not implement OBJ face incidence or coordinate welding.

No technical performance benchmark, speed/memory superiority or exhaustive feature-gap claim is made. Standard file formats and algorithms are not inventions of this project. Source references informed semantic review; implementation, prose and invented fixtures are original. No copied branding or sample user data is included.
