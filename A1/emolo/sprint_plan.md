

Before Sprint Planning begins, successful teams typically perform a set of preparation activities to ensure the sprint can be planned efficiently and with minimal ambiguity.

## 1. Product Backlog Refinement (Grooming)

This is the most important pre-planning activity.

### Activities

* Review new requirements
* Clarify business objectives
* Break large epics into user stories
* Define acceptance criteria
* Remove obsolete items
* Prioritize backlog items
* Identify dependencies
* Estimate effort

### Deliverables

* Prioritized backlog
* Refined user stories
* Story point estimates
* Dependency list

### Participants

* Product Owner
* Scrum Master
* Development Team
* Business Stakeholders (optional)

---

## 2. Define Sprint Goal

The Product Owner should identify the primary business outcome for the upcoming sprint.

### Activities

* Review roadmap
* Review release objectives
* Identify highest-value features
* Align with stakeholders

### Deliverables

* Draft Sprint Goal

### Example

Instead of:

> Build login page

Use:

> Enable customer self-service onboarding through secure account creation.

---

## 3. Capacity Planning

Determine how much work the team can realistically complete.

### Activities

* Review team availability
* Account for:

  * PTO
  * Holidays
  * Training
  * Support responsibilities
  * Production releases

### Deliverables

* Team Capacity Report

### Example

| Team Member | Capacity Days |
| ----------- | ------------- |
| Developer A | 8             |
| Developer B | 10            |
| Developer C | 6             |
| QA Engineer | 8             |
| Total       | 32            |

---

## 4. Velocity Analysis

Review historical delivery performance.

### Activities

* Analyze last 3-5 sprints
* Review completed story points
* Identify trends
* Adjust expectations

### Deliverables

* Velocity Report

### Example

| Sprint    | Points Completed |
| --------- | ---------------- |
| Sprint 15 | 42               |
| Sprint 16 | 39               |
| Sprint 17 | 45               |
| Average   | 42               |

---

## 5. Dependency Identification

Determine work that depends on other teams, vendors, systems, or approvals.

### Activities

* Review cross-team dependencies
* Review architecture dependencies
* Review infrastructure dependencies
* Review vendor dependencies

### Deliverables

* Dependency Matrix

| Story               | Dependency        | Owner         |
| ------------------- | ----------------- | ------------- |
| Payment API         | Security Approval | Security Team |
| Reporting Dashboard | Data Feed         | Data Team     |

---

## 6. Technical Readiness Review

Ensure stories are technically ready.

### Activities

* Architecture review
* Design review
* Data model review
* API review
* Security review
* Infrastructure review

### Deliverables

* Technical Readiness Checklist
* Architecture Decisions

---

## 7. Risk Assessment

Identify risks before committing.

### Activities

* Review technical risks
* Review business risks
* Review staffing risks
* Review integration risks

### Deliverables

* Risk Register

| Risk                   | Probability | Impact |
| ---------------------- | ----------- | ------ |
| Third-party API delays | Medium      | High   |
| Key developer PTO      | High        | Medium |

---

## 8. Definition of Ready Validation

Verify stories meet readiness criteria.

### Typical Definition of Ready

A story must have:

* Business value defined
* Acceptance criteria
* Dependencies identified
* Story points assigned
* Technical approach discussed
* Test approach defined
* Required approvals obtained

### Deliverables

* Ready Stories List

---

## 9. Environment and Infrastructure Readiness

Confirm supporting systems are available.

### Activities

* Validate environments
* Verify CI/CD pipelines
* Check test data availability
* Verify cloud resources
* Verify access permissions

### Deliverables

* Environment Readiness Report

---

## 10. Review Previous Sprint Outcomes

Use lessons learned before planning the next sprint.

### Activities

* Review sprint metrics
* Review retrospective actions
* Review defects
* Review escaped defects
* Review blocked work

### Deliverables

* Sprint Performance Summary
* Action Item Status Report

---

# Sprint Planning Inputs

The following artifacts should be available before the planning meeting:

| Artifact                      | Required    |
| ----------------------------- | ----------- |
| Prioritized Product Backlog   | Yes         |
| Sprint Goal Draft             | Yes         |
| Story Estimates               | Yes         |
| Velocity Report               | Yes         |
| Capacity Report               | Yes         |
| Dependency Matrix             | Yes         |
| Technical Design Documents    | Recommended |
| Risk Register                 | Recommended |
| Definition of Ready Checklist | Yes         |
| Environment Readiness Report  | Recommended |

---

# Typical Sprint Planning Agenda

### Part 1 – What Will Be Done?

1. Review Sprint Goal
2. Review top backlog items
3. Clarify requirements
4. Confirm priorities
5. Select stories

### Part 2 – How Will It Be Done?

1. Break stories into tasks
2. Review dependencies
3. Review risks
4. Confirm capacity
5. Commit to sprint backlog

### Outputs

* Sprint Goal
* Sprint Backlog
* Task Breakdown
* Capacity Allocation
* Risk List
* Dependency Plan

---

# Enterprise-Scale Sprint Planning (Large Programs)

For large modernization programs such as COBOL-to-Java, SAS-to-Python, cloud migration, or AI transformation projects, add these activities before sprint planning:

### Architecture Readiness Review

* Architecture decisions approved
* Integration points identified
* Non-functional requirements defined

### Data Readiness Assessment

* Source systems identified
* Data lineage documented
* Data quality assessed

### Compliance Review

* Security requirements
* Regulatory requirements
* Audit requirements

### Migration Readiness Assessment

* Application inventory
* Dependency maps
* Conversion candidates
* Proof-of-concept results

### Release Readiness Alignment

* Sprint objectives aligned to release milestones
* Deployment windows confirmed
* Rollback strategy reviewed

These additional activities significantly reduce sprint failure risk in large-scale enterprise transformation initiatives.
