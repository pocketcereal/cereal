# Master Domain List

First-pass domain extraction from `TODO.md`. This names architecture pieces
already implied by the idea; it does not refine scope or change the product
direction.

1. Video Source Runtime
   Opens configured video sources and provides frames for background processing.

2. Real-Time Processing Loop
   Runs continuously over active video so detections are captured before a user
   asks a question.
   Future architecture target: background detection runs continuously over
   active Sources.

3. YOLO Detection Pipeline
   Uses a conventional object detector, likely Ultralytics YOLO, to identify
   objects in frames.

4. Detection Event Store
   Persists detected objects, timestamps, source identity, classes, bounding
   regions, and confidence scores.
   First implementation focus: persist real YOLO-backed **Detection events**
   before adding agents, vectors, or tracking.
   First slice: run detection over the first configured Source and persist
   events; this proves the store before adding the background runtime.
   Detection events must retain evidence references back to the recorded video
   or original file so later validation can replay the relevant frames.

5. Temporal Object Tracking
   Connects detections across frames so repeated sightings can become one
   observed object or event.
   First detection slice stores an optional track identifier but defers
   Object track creation and count semantics to a later pass.

6. Confidence and Evidence Scoring
   Tracks detector confidence and later validation confidence so answers can be
   grounded in ranked evidence.

7. Frame Evidence Retrieval
   Finds relevant frames or frame windows around detections for deeper review by
   VLM agents.

8. Semantic Index
   Supports vector or metadata search over detections, tags, frame evidence, and
   related observations.

9. Query Understanding
   Turns user questions into time ranges, object classes, filters, grouping
   logic, and validation needs.

10. Main Agent Orchestrator
    Plans the answer, chooses tools, queries stored detections, and delegates
    specialized work.

11. Dynamic Agent Framework
    Provides structure for the main agent to create role-specific agents with
    constrained jobs and clear reporting contracts.

12. Specialist VLM Agents
    Validate focused visual claims, such as whether a candidate truck is white
    or whether an object is truly a truck.

13. Grouping and Correlation Logic
    Groups detections into candidate answers and discovers related conditions or
    emergent tags.

14. Structured Reporting
    Produces the final answer in a predictable structure with counts, evidence,
    timestamps, and validation details.

15. Model Integration Layer
    Isolates calls to YOLO, VLMs, Deep Agents, and future model providers behind
    narrow boundaries.

16. Background Job Runtime
    Owns long-running detection work, model execution, retries, and coordination
    outside direct user requests.

17. Time and Source Scope Model
    Defines how questions map to source selection, clock ranges, timestamps, and
    stored evidence windows.
