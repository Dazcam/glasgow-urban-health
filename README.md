# Glasgow Urban Health Navigator
### Bridging Computational Biology and Urban Analytics

**Project Overview**
This project applies high-performance genomic pipeline principles to urban socio-economic data. By correlating health deprivation (SIMD 2020) with green space accessibility (OSM), it demonstrates a reproducible workflow for urban resilience research.

**Engineering Highlights**
* **Containerization:** Built and deployed using Singularity (HPC) and Docker (Local) to ensure environment parity.
* **Spatial Ingestion:** Developed a custom Python pipeline to convert OSM-JSON into GeoJSON, performing spatial joins to map 'Environmental Stimuli' to 'Socio-Economic Cells'.
* **HPC Workflow:** Processed 6,000+ data zones using vectorized operations in a cluster environment, optimizing for memory efficiency.

**The "Bio" Analogy**
*In this project, I treat the city of Glasgow as a tissue sample. The Data Zones act as individual 'cells', the SIMD indices represent 'phenotypic markers', and the green space data represents 'environmental exposures'. My decade of experience in spatial transcriptomics allows me to analyze these urban patterns with the same rigor required for clinical genomic data.*
