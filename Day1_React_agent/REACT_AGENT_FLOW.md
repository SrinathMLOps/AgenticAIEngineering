# ReAct Agent — Full Flow Explained for Beginners

For beginners, don't think about the files first. Think about the journey of the user's question.

---

## User enters:
```
10+20
```

---

## Step 1: main.py starts the application

**Code:**
```python
from agent.runner import run

if __name__ == "__main__":
    run()
```

**Think:** 👉 This is the ON button of the application. Like:
```
Press Power Button
    ↓
Application Starts
```

---

## Step 2: runner.py receives the user's question

**Code:**
```python
task = input("Ask me something:")
```

**User types:**
```
10+20
```

**Now:**
```python
task = "10+20"
```

**Think:** 👉 The application has received the user's request. Like:
```
Customer:
I need something.

Shopkeeper:
Okay, tell me.
```

---

## Step 3: runner.py sends the request to loop.py

**Code:**
```python
result = react_loop(task)
```

**Current value:**
```python
react_loop("10+20")
```

**Think:** 👉 Runner doesn't know how to solve the problem. 👉 It sends the problem to the brain. Like:
```
Receptionist
    ↓
Manager
```

---

## Step 4: loop.py becomes the brain

**Code:**
```python
if "weather" in task:
```

**Check:**
```python
"weather" in "10+20"
```

**Result:**
```
False
```

**Next:**
```python
elif "+" in task
```

**Check:**
```python
"+" in "10+20"
```

**Result:**
```
True
```

**Think:** 👉 Brain understands this is a maths problem. Like:
```
Manager:
This looks like a calculation.
I need the calculator worker.
```

---

## Step 5: loop.py asks registry.py for the correct tool

**Code:**
```python
TOOLS["calculator"]
```

**Registry:**
```python
TOOLS = {
    "calculator": calculator,
    "weather": get_weather
}
```

**Think:** 👉 Registry is like a company employee directory. Like:
```
Who can solve calculations?

Registry:
Calculator Team.
```

---

## Step 6: calculator.py solves the problem

**Code:**
```python
calculator("10+20")
```

**Inside:**
```python
result = eval("10+20")
```

**Python calculates:**
```
30
```

**Returns:**
```python
"30"
```

**Think:** 👉 Worker finishes the job. Like:
```
Calculator Employee:
Answer is 30.
```

---

## Step 7: Result goes back to loop.py

**Code:**
```python
return "30"
```

**Think:** 👉 Worker gives answer back to manager.
```
Calculator
    ↓
Manager
```

---

## Step 8: loop.py returns result to runner.py

**Code:**
```python
return result
```

**Think:** 👉 Manager gives answer back to receptionist.
```
Manager
    ↓
Receptionist
```

---

## Step 9: runner.py prints the answer

**Code:**
```python
print(result)
```

**Output:**
```
30
```

**Think:** 👉 Receptionist tells customer.
```
Customer asks:
10+20

Customer receives:
30
```

---

## Entire Flow in One Picture

```
User
 |
 ▼
10+20

 |
 ▼

main.py
(Start Application)

 |
 ▼

runner.py
(Take User Input)

 |
 ▼

loop.py
(Brain/Decision Maker)

 |
 ▼

registry.py
(Find Correct Tool)

 |
 ▼

calculator.py
(Solve Problem)

 |
 ▼

30

 |
 ▼

loop.py

 |
 ▼

runner.py

 |
 ▼

Print Result

 |
 ▼

User sees:

30
```

---

## Easiest way to remember

```
main.py       = Start Button

runner.py     = Receptionist

loop.py       = Manager / Brain

registry.py   = Employee Directory

calculator.py = Calculator Employee

memory.py     = Notebook

User          = Customer
```

---

**If you can explain "Customer → Receptionist → Manager → Employee → Manager → Receptionist → Customer", you can explain the entire ReAct agent flow in an interview.**
