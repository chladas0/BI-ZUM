(define (domain mapf)
  (:predicates
     (occupied  ?x)
     (connected ?x ?y)
     (at ?vertex ?agent)
     )

(:action move
    ; Which agent move from -> to
	:parameters (?agent ?from ?to)

    ; Agent is located at from, from is occupied and to is not occupied
	:precondition
	(and 
    	(occupied ?from) 
    	(not(occupied ?to))
    	(connected ?from ?to)
    	(at ?from ?agent)
	)

    ; Move the agent from -> to, set from as not occupied and to as occupied
	:effect
	(and 
    	(not (occupied ?from))
    	(occupied ?to)
        (not (at ?from ?agent))
        (at ?to ?agent)
	)
	
))
