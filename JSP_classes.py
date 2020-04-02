class operation:
    def __init__(self,name,duration):
        self.name=name
        self.duration=duration

class resource:
    def __init__(self,name,capacity):
        self.name=name
        self.capacity=capacity

class allocation:
    def __init__(self,resource,operation):
        self.resource=resource
        self.operation=operation

class relation:
    def __init__(self,op1,op2):
        self.op1=op1
        self.op2=op2