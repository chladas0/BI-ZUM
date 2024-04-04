(define (problem simple-problem)
  (:domain mapf)
  (:objects
    agent1 agent2 agent3
    vertex1 vertex2 vertex3 vertex4 vertex5 vertex6
  )
  
  (:init
  ; The undirected graph
  (connected vertex1 vertex2)
  (connected vertex2 vertex1)
  
  (connected vertex2 vertex3)
  (connected vertex3 vertex2)
  
  (connected vertex2 vertex4)
  (connected vertex4 vertex2)

  (connected vertex6 vertex4)
  (connected vertex4 vertex6)

  (connected vertex5 vertex4)
  (connected vertex4 vertex5)

  
  ;Agents positions
  (at vertex1 agent1)
  (at vertex4 agent2)
  (at vertex6 agent3)
  
  (occupied vertex1)
  (occupied vertex4)
  (occupied vertex6)
  )
   
  (:goal
    (and
    (at vertex5 agent1)
    (at vertex1 agent2)
    (at vertex3 agent3)
    )
  )
)
