# Simple Automata Theory algorithms for AGH course

* e-NFA to DFA conversion
* DFA minimization 
* CYK algorithm
* Automata visualization


## Examples

<details>
    <summary>
      
  ### conversion to deterministic
      
  </summary>
 
  #### 1
  input
  ```
  table = {
      0: {'0': {1}},
      1: {TransitionFunction.Epsilon: {2}},
      2: {'1': {3}},
      3: {TransitionFunction.Epsilon: {2, 4}},
      4: {TransitionFunction.Epsilon: {1},
          '0': {5}},
      5: {}
  }

  func = TransitionFunction(
      table,
      {5},
      0
  )
  func_converted = func.convert_to_deterministic()
  ```
  output
  ```
  STARTING {0}

  CONVERTED TO DETERMINISTIC
  {0} ---> {
            0 --> {1 2},
            1 --> {},
            }
  {} ---> {
           0 --> {},
           1 --> {},
           }
  {1 2} ---> {
              0 --> {},
              1 --> {1 2 3 4},
              }
  {1 2 3 4} ---> {
                  0 --> {5},
                  1 --> {1 2 3 4},
                  }
  {5} ---> {
            0 --> {},
            1 --> {},
            }

  ACCEPTING STATES
  {5}
  ```
  #### 2
  input
  ```
  table = {
      0: {'a': {1}},
      1: {'a': {2}},
      2: {TransitionFunction.Epsilon: {3}},
      3: {TransitionFunction.Epsilon: {4, 6}},
      4: {'a': {5}},
      5: {TransitionFunction.Epsilon: {8}},
      6: {'b': {7}},
      7: {TransitionFunction.Epsilon: {8}},
      8: {TransitionFunction.Epsilon: {3, 9}},
      9: {'b': {10}},
      10: {}
  }

  func = TransitionFunction(
      table,
      {10},
      0
  )
  func_converted = func.convert_to_deterministic()
  ```
  output
  ```
  STARTING {0}

  CONVERTED TO DETERMINISTIC
  {0} ---> {
            b --> {},
            a --> {1},
            }
  {} ---> {
           b --> {},
           a --> {},
           }
  {1} ---> {
            b --> {},
            a --> {2 3 4 6},
            }
  {2 3 4 6} ---> {
                  b --> {3 4 6 7 8 9},
                  a --> {3 4 5 6 8 9},
                  }
  {3 4 6 7 8 9} ---> {
                      b --> {3 4 6 7 8 9 10},
                      a --> {3 4 5 6 8 9},
                      }
  {3 4 5 6 8 9} ---> {
                      b --> {3 4 6 7 8 9 10},
                      a --> {3 4 5 6 8 9},
                      }
  {3 4 6 7 8 9 10} ---> {
                         b --> {3 4 6 7 8 9 10},
                         a --> {3 4 5 6 8 9},
                         }

  ACCEPTING STATES
  {3 4 6 7 8 9 10}
  ```
</details>



<details>
    <summary>
      
  ### visualization
      
  </summary>
  
  #### 1
  input
  
  ```
  func2 = TransitionFunction(
      {
          'q1': {'0': {'q1'},
                 '1': {'q1', 'q2'}},

          'q2': {'0': {'q3'},
                 '1': {}},

          'q3': {'0': {},
                 '1': {}},
      },
      {'q3'},
      'q1'
  )
  func_converted2 = func2.convert_to_deterministic()

  automata2 = FiniteAutomata(func2)

  automata2.run('0110')
  automata2.visualizer.show()
  ```
  output
  ```
  START q1
  STATES [q1] L 0
  STATES [q1] L 1
  STATES [q2, q1] L 1
  STATES [q2, q1] L 0
  STATES [q3, q1]
  True
  ```
  
  ![image](https://user-images.githubusercontent.com/64007876/177417841-bec1c51a-5538-453f-9d13-2aa027b16eef.png)


</details>

