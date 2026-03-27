<h2 align="center">Compute Paradigm Benchmarking</h2>
<h3 align="center">Classical vs. Quantum-Inspired Optimization</h3>

## Overview
This analysis was developed following an industry workshop led by a guest speaker from NVIDIA, focusing on approaches to analyzing complex data such as high-performance compute optimization.

This repository contains a comparative performance analysis of three distinct computational approaches.
Standard Classical, Complex Classical, and Quantum-Inspired. **(experiment data given is synthetic)**

The purpose of this project is to evaluate how different computing architectures balance accuracy against execution time and hardware resource consumption.


## Problem-First Approach
Before jumping right into analysis and visualization, I tried to make sure I understand the relational context of what's given.

1. Root Cause Analysis

Instead of starting with "How do I build a dashboard?", I started with "Why does this problem exist?" 

* **The Problem**: High-performance computing is expensive. Organizations need to know if the accuracy gain of a complex model justifies the exponential increase in energy and time costs.<br/>
* **The Goal**: Identify the "Economic Inflection Point" where Quantum approaches provide the best Return on Compute (ROC).


2. Establishing Relational Context

I evaluated the dataset by asking: How does this data relate to what I already know about high-performance computing?

* **Information Audit**: I mapped out the available metrics (Memory MB, Energy Units, Objective Scores) to see if they provided a full picture of "Efficiency" rather than just "Accuracy." <br/>
* **Contrast**: I analyzed how "Complex Classical" (GPU-level) differed from "Standard Classical" (CPU-level) to establish a baseline for the Quantum results.


3. Iterative Strategy & Refinement
* **Multiple Approaches**: I tested several ways to define "success" by looking at final score vs. looking at "Time-to-Convergence."
* **Testing against Problem Statement**: I validated these approaches against the core question: Which architecture is best for a real-time, resource-constrained environment?

## Data Insights & Benchmarking Results
From the analysis of the experimental data, the following insights were derived:

* Best objective performance: Complex Classical with an average final best objective score of 96.67.
* Fastest execution: Quantum Approach with average elapsed time of 63.55.
* Most stable: Complex Classical with average stability score of 93.03%.
* Lowest noise/error: Complex Classical with average error/noise of 3.00%.

Key Findings:
* The "Quantum Efficiency" Gap: The Quantum approach achieved 84% of peak accuracy while utilizing 55% less energy and running 62% faster than the high-complexity classical model.
* Scalability Bottlenecks: The Complex Classical model showed exponential memory growth (643MB), suggesting high overhead for large-scale deployments.
* The Sweet Spot: For applications where sub-second latency and power efficiency are prioritized over absolute 99th-percentile precision, the Quantum approach is the superior architectural choice.

<img width="1306" height="724" alt="image" src="https://github.com/user-attachments/assets/de3df3f9-4e26-4182-abc7-a60bd19c7082" />

-Image from streamlit dashboard (Best objective score as metric)-

## What's Next? (What Matters the Most)

To move this from a benchmark to a production-ready recommendation to business decisions, the next phases include:
1. Dynamic Scaling Tests: Testing the Quantum approach on larger datasets to see if the memory efficiency remains linear.
2. Cost-Benefit Modeling: Integrating dollar-per-compute-hour metrics to translate "Energy Units" into actual budget savings.

**Communication for Business Team**
From a certain number of iterations (computational cycle), the graph of quantum approach flattens whereas complex classical keeps increasing. While the complex classical model show marginal gains in performance and accuracy, it does so in using resources as well.

The quantum approach is superior in accuracy-to-energy ratio which makes it suitable for a sustainable path and scalability.

**For Precision: Complex Classical.**


**For Sustainability & Scalability: Quantum.**

## Run the Dashboard yourself
**Installation**

Clone the repository:
<pre><code>
git clone https://github.com/jrhie22/compute-paradigm-benchmarking.git
cd compute-paradigm-benchmarking
</code></pre>

<pre><code>
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
</code></pre>

Install Dependencies
<pre><code>
pip install -r requirements.txt
</code></pre>

Run Dashboard
<pre><code>
streamlit run streamlit_experiment_dashboard.py
</code></pre>
