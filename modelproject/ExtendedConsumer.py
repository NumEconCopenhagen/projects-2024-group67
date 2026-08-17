import numpy as np
from Consumer import ConsumerClass

class ExtendedConsumerClass(ConsumerClass):
    """ consumer with Stone-Geary preferences (subsistence level for food) """
    
    def setup(self):
        """ set the baseline parameters including subsistence """
        
        # a. inherit baseline parameters
        super().setup()
        
        # b. add subsistence level
        self.par.x1_bar = 2.0 # minimum food requirement

    def quantities(self, s1, w):
        """ the quantities implied by the nested shares and subsistence """
        
        par = self.par
        
        # a. compute discretionary income
        I_disp = par.I - (par.p1 * par.x1_bar)
        
        # b. get shares of discretionary income
        s1_share, s2_share, s3_share = self.shares(s1, w)
        
        # c. compute total quantities
        x1 = par.x1_bar + (s1_share * I_disp) / par.p1
        x2 = (s2_share * I_disp) / par.p2
        x3 = (s3_share * I_disp) / par.p3
        
        return x1, x2, x3
        
    def utility(self, x1, x2, x3):
        """ utility evaluated over discretionary consumption """
        
        par = self.par
        
        # a. travel composite
        x_travel = self.ces(x2, x3, par.beta, par.sigma_B)
        
        # b. discretionary food consumption
        x1_disp = np.maximum(x1 - par.x1_bar, par.s_min) 
        
        # c. total utility
        u = self.ces(x1_disp, x_travel, par.alpha, par.sigma_A)
        
        return u
        
    def value_of_choice(self, s1, w):
        """ utility of the bundle implied by the nested shares """
        
        # a. compute quantities
        x1, x2, x3 = self.quantities(s1, w)
        
        # b. compute and return utility
        return self.utility(x1, x2, x3)