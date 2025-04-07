## Baseline strategies

We establish 6 baseline strategies that we can use to gauge the negotiation performance of LLMs before we move on to human trials. All algorithms are designed from the buyer's perspective (LLM seller vs human buyer scenario). We assume that the initial price proposed by the seller is given. 

#### 1. Fixed Concession Strategy

Make equal amount of concessions at each iteration

***Algorithm***  

```
variables = x, y  

expected_cost_of_production = initial_price * x%  
concession = expected_cost_of_production * y%  
for t in 0...T:  
    offer = expected_cost_of_production + concession * t  
    yield offer  
```

##### 1.1 Strong Anchoring + Gradual Concessions

Low x, low y

#### 2. Decrementing Concession Strategy 

Decrease the amount of concession at each iteration

***Algorithm***  

```
variables = x, y, z  

expected_cost_of_production = initial_price * x%  
initial_concession = expected_cost_of_production * y%  
concession_decay = z%  
offer = expected_cost_of_production  
for t in 0...T:  
    new_offer = offer + initial_concession * (1 - z)^t  
    offer = new_offer  
    yield offer  
```

##### 2.1 Theory of Mind

Give the impression that you are running out of room for negotiation 

High z 

#### 3. Reciprocal Concession Strategy

Mirror the amount of concession the opponent makes at each iteration. 

***Algorithm***

```
variables = x

expected_cost_of_production = initial_price * x%  
counter_offer = get_counter_offer(t = 0)  
offer = expected_cost_of_production  
for t in 0...T:  
    new_counter_offer = get_counter_offer(t)   
    offer = offer + new_counter_offer - counter_offer   
    counter_offer = new_counter_offer  
    yield offer
```


#### 4. No Concession Strategy 

Make no concessions at each iteration

***Algorithm***

```
variables = x, y

expected_cost_of_production = initial_price * x%  
initial_price = expected_cost_of_production + (willingness_to_pay - expected_cost_of_production) * y% 
for t in 0...T:  
    offer = initial_price
    yield offer
```

If $y = 0.5$, we can mimic "fair" hardline strategy


#### 5. Randomized Concession Strategy 

Randomize the amount of concession at each iteration

***Algorithm***  

```
variables = x, d

expected_cost_of_production = initial_price * x%  
d = func(distribution)
offer = expected_cost_of_production  
for t in 0...T:  
    new_offer = offer + d(t)   
    offer = new_offer  
    yield offer  
```

Where $d$ is a function that determines the amount of concession at time $t$

### Variations

Below are derivations of the aforementioned strategies.

#### 6. Deadline Pressure Strategy 

Hardline until the very end and make small concessions for the last few iterations.

***Algorithm***  

```
variables = x, y, z  

expected_cost_of_production = initial_price * x%  
iterations_to_engage = y
concession = expected_cost_of_production * z%  
for t in 0...T:  
    if T - t < iterations_to_engage:
        offer =  expected_cost_of_production + concession * (iterations_to_engage - (T - t))
    else: 
        offer = expected_cost_of_production
    yield offer  

```

