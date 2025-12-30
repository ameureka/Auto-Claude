# Implementation Plan

- [ ] 1. Set up project structure and core interfaces
  - Create directory structure: `src/models`, `src/services`, `src/storage`, `src/components`
  - Define TypeScript interfaces for Task, TaskManager, TaskStore, LocalStorageAdapter
  - Set up Vitest with fast-check for property testing
  - _Requirements: 1.1, 4.1_

- [ ] 2. Implement data models and validation
- [ ] 2.1 Create Task model and validation functions
  - Implement Task interface with id, description, completed, createdAt, updatedAt
  - Create `validateDescription()` function for non-empty, non-whitespace validation
  - Create `createTask()` factory function with UUID generation
  - _Requirements: 1.1, 1.2_

- [ ]* 2.2 Write property test: Task addition increases list length
  - **Property 1: Task addition increases list length**
  - **Validates: Requirements 1.1**

- [ ]* 2.3 Write property test: Whitespace rejection
  - **Property 2: Whitespace-only descriptions are rejected**
  - **Validates: Requirements 1.2**

- [ ] 3. Implement LocalStorage adapter
- [ ] 3.1 Create LocalStorageAdapter with serialize/deserialize
  - Implement `save(tasks: Task[]): void` with JSON serialization
  - Implement `load(): Result<Task[], ParseError>` with error handling
  - Handle invalid JSON gracefully (return empty array)
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 3.2 Write property test: Persistence round-trip
  - **Property 5: Persistence round-trip**
  - **Validates: Requirements 4.1, 4.3**

- [ ]* 3.3 Write property test: Invalid data recovery
  - **Property 6: Invalid data recovery**
  - **Validates: Requirements 4.2**

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement TaskStore
- [ ] 5.1 Create TaskStore with state management
  - Implement `getAll()`, `getById()`, `add()`, `update()`, `remove()` methods
  - Implement `subscribe()` for reactive updates
  - Integrate with LocalStorageAdapter for persistence
  - _Requirements: 1.1, 2.1, 3.1_

- [ ] 5.2 Implement task toggle functionality
  - Add `toggleCompleted(id: string)` method
  - Ensure state update triggers persistence
  - _Requirements: 2.1, 2.2_

- [ ]* 5.3 Write property test: Toggle involution
  - **Property 3: Toggle is an involution**
  - **Validates: Requirements 2.1**

- [ ] 5.4 Implement task deletion
  - Add `delete(id: string)` method
  - Ensure state update triggers persistence and UI notification
  - _Requirements: 3.1, 3.2, 3.3_

- [ ]* 5.5 Write property test: Deletion removes exactly one task
  - **Property 4: Deletion removes exactly one task**
  - **Validates: Requirements 3.1, 3.3**

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement TaskManager
- [ ] 7.1 Create TaskManager as facade
  - Implement `createTask()`, `toggleTask()`, `deleteTask()` methods
  - Add input validation before delegating to TaskStore
  - Return Result types for error handling
  - _Requirements: 1.1, 1.2, 2.1, 3.1_

- [ ] 7.2 Implement filtering functionality
  - Add `getTasks(filter?: TaskFilter)` method
  - Implement filter logic for 'all', 'active', 'completed'
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 7.3 Write property test: Filter correctness
  - **Property 7: Filter correctness**
  - **Validates: Requirements 5.1, 5.2, 5.3**

- [ ] 8. Implement UI components
- [ ] 8.1 Create TaskInput component
  - Handle Enter key press for task submission
  - Clear input and maintain focus after submission
  - Integrate with TaskManager.createTask()
  - _Requirements: 1.1, 1.3_

- [ ] 8.2 Create TaskList component
  - Display tasks with checkbox and delete button
  - Apply strikethrough style for completed tasks
  - Subscribe to TaskStore for reactive updates
  - _Requirements: 2.3, 3.3_

- [ ] 8.3 Create FilterBar component
  - Implement filter buttons for 'all', 'active', 'completed'
  - Highlight active filter
  - _Requirements: 5.1, 5.2, 5.3_

- [ ]* 8.4 Write unit tests for UI components
  - Test TaskInput submission and clearing
  - Test TaskList rendering with various states
  - Test FilterBar filter switching
  - _Requirements: 1.3, 2.3, 5.4_

- [ ] 9. Integration and final testing
- [ ] 9.1 Wire up all components
  - Create main App component
  - Initialize TaskManager with LocalStorage
  - Connect all UI components
  - _Requirements: All_

- [ ]* 9.2 Write integration tests
  - Test full flow: add → toggle → delete
  - Test persistence across page reload simulation
  - Test filter interactions
  - _Requirements: All_

- [ ] 10. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

This task list demonstrates:

1. **Two-level hierarchy**: Top-level tasks (epics) and sub-tasks with decimal numbering

2. **Optional task marking**: Test-related sub-tasks marked with `*`

3. **Property test placement**: Property tests immediately follow related implementation

4. **Requirement references**: Each task references specific requirements

5. **Checkpoints**: Strategic checkpoints after major milestones

6. **Property annotations**: Each property test task includes:
   - Property number and name
   - Validates reference to requirements

7. **No non-coding tasks**: All tasks involve writing, modifying, or testing code
