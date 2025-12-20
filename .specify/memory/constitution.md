<!-- Sync Impact Report
Version change: N/A → 1.0.0
List of modified principles: All principles added
Added sections: Hardware Requirements, Development and Usage Guidelines
Removed sections: None
Templates requiring updates: plan-template.md (Constitution Check updated), spec-template.md (no changes), tasks-template.md (no changes), commands (none exist), README.md (no changes)
Follow-up TODOs: None
-->
# Lego Brick Detection Constitution

## Core Principles

### Accurate Lego Brick Spotting
Spot Lego bricks in a pile of Lego pieces. This principle ensures easy and accurate identification of target bricks, simplifying the user's task of finding specific pieces.

### Set-Based Brick Definition
The Lego bricks to detect are defined from the set pieces of a Lego set. This allows for straightforward configuration using predefined inventories, enhancing usability by avoiding manual brick specification.

### No Re-detection After Pickup
Once the Lego brick has been physically picked up, it should not be detected again. This prevents redundant detections, making the building process smoother and more user-friendly.

### Real-Time Video Input
The input is coming from a Kinect (nominal) or a webcam (nominal) => Video stream. Utilizing standard hardware for real-time input ensures easy setup and continuous detection without complex configurations.

### Robust Environmental Detection
The detection should work in various lighting conditions and angles. Eventually, the input can be a static image (less important) => Static input. This robustness promotes ease of use across different scenarios and environments.

## Hardware Requirements

If required, the hardware is 
 - Kinect v1 (Xbox 360)
 - GPU : RTX 4070

## Development and Usage Guidelines

Focus on simplicity and ease of use in all implementations. Ensure that the system is intuitive for users to set up and operate.

## Governance

Constitution supersedes all other practices; Amendments require documentation, approval, and migration plan. All changes must verify compliance with principles focused on easiness of usage.

**Version**: 1.0.0 | **Ratified**: 2025-12-20 | **Last Amended**: 2025-12-20
