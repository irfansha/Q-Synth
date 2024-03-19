# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

# Copied from Q-sage repository

'''
Creates an object with next var + 1 and dispatches given
number of variables as a list.
'''
class VarDispatcher():


  def get_vars(self, n):
    var_list = list(range(self.next_var, self.next_var+n))
    self.next_var = self.next_var+n
    return var_list

  def get_single_var(self):
    cur_var = self.next_var
    self.next_var += 1
    return cur_var

  def set_next_var(self, n):
    self.next_var = n

  def __init__(self):
    self.next_var = 1