3. ukol -> Varianta(a) -> Popis ulohy v PPDL a generovani planu z existujiciho planovace 
 - Univerzum -> agent, vertex
 - Predikaty -> at(agent, vertex), free(vertex), goal(agent, vertex), occupied(vertex), connected(v1, v2)
 - Actions -> move(who, from, where), 





Zadani:
MAPF (Multi-agentní hledání cest, Multi-agent Path Finding)
Úloha se podobá Lišákovi s tím, že místo mřízky máme obecný souvislý neorientovaný graf. Místo dlaždic (bloků) máme očíslované agenty, kteří jsou ve vrcholech, vždy nejvýše jeden agent ve vrcholu. Nějaké vrcholy jsou volné a podobně jako u Lišáka, je možný tah agentem do sousedního volného vrcholu. Cílem je najít posloupnost tahů tak, aby každý agent dorazil do svého cílového vrcholu.
