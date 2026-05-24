# Single Cell Modelling
* Overview of Electrified Systems Design Engineer Professional Certificate
* Introduction to Battery Design and Management
* Modeling a Single Battery Cell
* Guided Lesson - Simulating a Battery Discharge Circuit
* Safely Charging a Battery Cell
* Practice with a Charging Algorithm
* Modeling a Single Cell
* Charging Algorithms

# Cell Characterization & Battery Pack Modeling
* Introduction to Cell Characterization
* Simulating a Characterized Cell
* Introduction to Battery Pack Modeling
* Building an E-Scooter Battery Pack
* Model Resolution and Measurements in Battery Packs
* Thermal Modeling in Battery Packs
* Cell Characterization
* Battery Pack Modeling

# Battery Management Systems
1.1.2: Introducing Important Battery Terminology•18 minutes
1.1.3: What Are the Parts of an Electrochemical Cell?•22 minutes
1.1.4: How Does an Electrochemical Cell Store and Release Energy?•20 minutes
1.1.5: What Are the Best Materials to Use in an Electrochemical Cell?•23 minutes
1.1.6: Example Electrochemical (incl. PbA and NiMH) Cells•25 minutes
1.1.7: Summary of "Battery Boot Camp" Module plus Next Steps•4 minutes

* Overview of Battery Management Systems
* Battery State Estimation
* State Estimation of the E-Scooter Battery Pack
* Cell Balancing Algorithms
* Cell Balancing of the E-Scooter Battery Pack 
* State Estimation 
* Cell Balancing

# Lithium-Ion Cells
The principal advantages of lithium-ion cells versus standard electrochemical battery cells, what are their primary components, and how they work.
1.2.1: Benefits of Lithium-Ion Cells•13 minutes
1.2.2: What Makes Lithium-Ion Cells Different from Electrochemical Cells?•19 minutes
1.2.3: Negative Electrodes for Lithium-Ion Cells•23 minutes
1.2.4: Positive Electrodes for Lithium-Ion Cells•21 minutes
1.2.5: Electrolytes and Separators for Lithium-Ion Cells•15 minutes
1.2.6: Is Lithium Going to Run Out?•12 minutes
1.2.7: Summary of "How Lithium-Ion Cells Work" Module Plus Next Steps•4 minutes

# BMS Sensing and High-Voltage Control
Learn about BMS requirements, and will study the requirements for sensing and high-voltage control in detail.
1.3.1: What Are the Primary Functions of a BMS?•23 minutes
1.3.2: What Are Some Reasons for Modular Design?•33 minutes
1.3.3: How to Sense All Cell Voltages in a BMS?•26 minutes
1.3.4: How to Sense Module Temperature in a BMS?•16 minutes
1.3.5: How to Sense Battery-Pack Current in a BMS?•16 minutes
1.3.6: How to Control Contactors with a BMS?•14 minutes
1.3.7: How to Sense Electrical Isolation in a BMS?•16 minutes
1.3.8: How to Control Battery-Pack Temperature With a BMS?•14 minutes
1.3.9: Summary of "BMS Sensing and High-Voltage Control" Module plus Next Steps•3 minutes

# BMS Design Requirements
Learn about BMS requirements, studying requirements for protection, interface, performance management, and diagnostics in detail.
1.4.1: How Can a BMS Protect the User and Battery Pack?•15 minutes
1.4.2: How Must a BMS Interface with Other System Components?•17 minutes
1.4.3: Why Must a BMS Estimate SOC and SOH?•11 minutes
1.4.4: What Are Cell SOC and Battery-Pack SOC?•20 minutes
1.4.5: How Do I Compute Cell Available Energy and Power?•18 minutes
1.4.6: How Do I Compute Battery-Pack Available Energy and Power?•16 minutes
1.4.7: What Kinds of Diagnostics Must a BMS Report?•7 minutes
1.4.8: Summary of "BMS Design Requirements 2-5" Module plus Next Steps•5 minutes

# Making Cells
How lithium-ion cells are made and how they can fail
1.5.1: How Are a Lithium-Ion Cell’s Electrodes Fabricated?•12 minutes
1.5.2: How is a Lithium-Ion Cell Assembled?•21 minutes
1.5.3: What Are Normal Lithium-Ion Cell Aging Processes?•16 minutes
1.5.4: What Are Abnormal Cell Aging Processes and Failure Modes?•11 minutes
1.5.5: Summary of "How Are Cells Made? How Can They Fail?" Module plus Next Steps•3 minutes



## Skills
	* Control Systems
	* Electrical Engineering
	* Electrical Power
	* Electrical Safety
	* Electrical Systems
	* Electronic Components
	* Electronics
	* Estimation
	* Failure Analysis
	* High Voltage
	* Low Voltage
	* Mathematical Modeling
	* Model Evaluation
	* Model Optimization
	* Power Electronics
	* Safety Standards
	* Simulation and Simulation Software
	* Simulations
	* Thermal Management

## Aims
* How to design equivalent-circuit models for lithium-ion battery cells
* How to implement state-of-charge (SOC) estimators for lithium-ion battery cells
* How to implement state-of-health (SOH) estimators for lithium-ion battery cells
* How to design balancers and power-limits estimators for lithium-ion battery packs

# Stateflow, Advanced Concepts.
* Implementing Battery Management Ssystem (BMS) Logic with Stateflow
* Cycle Testing the E-Scooter Battery Pack
* Advanced Topics in Battery Design and Management
* Battery Module Design
* Module Discharge Behavior
* Charging the Module

## 


# Battery Pack Balancing and Power Estimation
How to design balancers and power-limits estimators for lithium-ion battery packs

## Passive balancing methods for battery packs 
how to write algorithms for two primary control tasks: balancing and power-limits computations. This week, you will learn why battery packs naturally become unbalanced, some balancing strategies, and how passive circuits can be used to balance battery packs.

* 5.1.2: Introduction to battery-pack balancing•10 minutes
5.1.3: How do battery packs become imbalanced?•16 minutes
5.1.4: What are the criteria for specifying a balancing setpoint for a battery pack?•14 minutes
5.1.5: What are the criteria for specifying when to balance a battery pack?•13 minutes
5.1.6: What kinds of circuits can be used for passively balancing a battery pack?•16 minutes
5.1.7: Summary of "Passive balancing methods for battery packs"; what next?•3 minutes

## Active balancing methods for battery packs
Passive balancing can be effective, but wastes energy. Active balancing methods attempt to conserve energy and have other advantages as well. Learn about active-balancing circuitry and methods.

5.2.1: How to balance actively using capacitor-based circuits•12 minutes
5.2.2: How to balance actively using transformer-based circuits•8 minutes
5.2.3: How to balance actively using a shared active bus•15 minutes
5.2.4: Using simulation to show how quickly we must balance a battery pack•14 minutes
5.2.5: Introducing Octave code to simulate balancing: The main program loop•22 minutes
5.2.6: Summary of "Active balancing methods for battery packs"; what next?•3 minutes

## How to find available battery power using a simplified cell model 
learn how to extend the method to satisfy limits on SOC, load power, and electronics current. You will learn how to implement the power-limits computation methods in Octave code.

5.3.1: What factors must we consider when finding available battery power?•14 minutes
5.3.2: How to compute available battery power based on cell terminal voltage•8 minutes
5.3.3: How to consider other performance limits when computing available battery power•8 minutes
5.3.4: Introducing Octave code to compute power limits using simplified cell model•13 minutes
5.3.5: Summary of "How to find available battery power using a simplified cell model"; what next?•2 minutes

## How to find available battery power using a comprehensive cell model
The HPPC method, even as extended last week, makes some simplifying assumptions that are not met in practice. This week, we explore a more accurate method that uses full state information from an xKF as its input, along with a full ESC cell model to find power limits. 

5.4.1: What factors must we consider when finding available battery power?•13 minutes
5.4.2: How to solve for a future battery condition using the bisection algorithm•11 minutes
5.4.3: How to use bisection to estimate available power using comprehensive cell model•17 minutes
5.4.4: Introducing Octave code to compute power limits using comprehensive cell model•9 minutes
5.4.5: Using simulation to compare and contrast different power-estimation methods•12 minutes
5.4.6: Concluding remarks for the specialization•6 minutes


## Future Battery-Management-System Algorithms
Present-day BMS algorithms primarily use equivalent-circuit models as a basis for estimating state-of-charge, state-of-health, power limits, and so forth. These models are not able to describe directly the physical processes internal to the cell. But, it is exactly these processes that are precursors to cell degradation and failure. This week quickly introduces some concepts that might motivate future BMS algorithms that use physics-based models instead.

5.5.1: What BMS algorithm needs remain?•21 minutes
5.5.2: Physics-based ideal-cell models•17 minutes
5.5.3: Single-particle reduced-order models•31 minutes
5.5.4: 1-d physics-based reduced-order models•20 minutes
5.5.5: Models of degradation mechanisms•18 minutes
5.5.6: Optimized controls using physics-based models•32 minutes


## 

## 

## 

## 

