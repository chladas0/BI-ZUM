(define (problem simple-problem)
  (:domain mapf)
  (:objects
    agent1 agent2 - agent
    vertex1 vertex2 vertex3 vertex4 - vertex
  )
  
  (:init
  ; The undirected graph
  (connected vertex1 vertex4)
  (connected vertex4 vertex1)
  
  (connected vertex4 vertex2)
  (connected vertex2 vertex4)
  
  (connected vertex4 vertex3)
  (connected vertex3 vertex4)
  
  ;Agents positions
  (at vertex1 agent1)
  (at vertex4 agent2)
  
  (occupied vertex1)
  (occupied vertex4)
  )
   
  (:goal
    (and
    (at vertex1 agent2)
    (at vertex2 agent1)
    )
  )
)
