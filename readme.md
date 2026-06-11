# ipycalcpad

## Arithmetic

```jupyterpython
%%calcpad
1 + 2**3
22/(1+2*5)
```

$1 + 2^3 = 9$

$\dfrac{22}{1+2\cdot5} = 2$

## Variables

```jupyterpython
%%calcpad
a = 12; b = 2.0
c = 2 + a ** b
```

$a=12,\quad b=2.0$

$c=2+a^b=146$

## Dataframes

### Dataframe Operations

```jupyterpython
%%calcpad
D['x'] = [1, 2, 3] # Dataframe assignment:
D['y'] = 2*D.x**2 # Column operation:
D['z'] = 3*D['y'] # Column operation:
```

&nbsp; Dataframe assignment: $\quad x = \begin{bmatrix}1\\2\\3\end{bmatrix}$

&nbsp; Column operation: $\quad y = 2\cdot x^2$

&nbsp; Column operation: $\quad z = 3\cdot y$

### Dataframe display

```jupyterpython
%%calcpad
D
```

|     | **x** | **y** | **z** |
|:---:|:-----:|:-----:|:-----:|
| *0* |   1   |   2   |   6   |
| *1* |   2   |   8   |  24   |
| *2* |   3   |  18   |  42   |