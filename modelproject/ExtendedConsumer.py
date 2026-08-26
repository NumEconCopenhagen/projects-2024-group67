import numpy as np
from Consumer import ConsumerClass

class ExtendedConsumerClass(ConsumerClass):
    """ consumer with subsistence level for food """
    
    def setup(self):
        """ set the baseline parameters including subsistence """
        
        # a. Starting with the baseline parameters:
        super().setup()
        
        # b. Adding the extention of the bare minimum food requirement:
        self.par.x1_bar = 2.0 # minimum food requirement

    def quantities(self, s1, w):
        """ calculates the quantities implied by the nested shares and subsistence 
        
        Args:
            s1 (float): budget share parameter for food
            w (float): budget share parameter for transport
            
        Returns:
            x1 (float): quantity of food
            x2 (float): quantity of bus transport
            x3 (float): quantity of train transport 
        """
        
        par = self.par
        
        # c. Computing the discretionary income:
        I_disp = par.I - (par.p1 * par.x1_bar)
        
        # d. extracting the shares of discretionary income
        s1_share, s2_share, s3_share = self.shares(s1, w)
        
        # e. computing the total quantities
        x1 = par.x1_bar + (s1_share * I_disp) / par.p1
        x2 = (s2_share * I_disp) / par.p2
        x3 = (s3_share * I_disp) / par.p3
        
        return x1, x2, x3
        
    def utility(self, x1, x2, x3):
        """ evaluates utility over discretionary consumption 
        
        Args:
            x1 (float): quantity of food
            x2 (float): quantity of bus transport
            x3 (float): quantity of train transport
            
        Returns:
            u (float): total utility    
        """
        
        par = self.par
        
        # f. the transport nest:
        x_travel = self.ces(x2, x3, par.beta, par.sigma_B)
        
        # g. discretionary food consumption
        x1_disp = np.maximum(x1 - par.x1_bar, par.s_min) 
        
        # h. total utility
        u = self.ces(x1_disp, x_travel, par.alpha, par.sigma_A)
        
        return u
        
    def value_of_choice(self, s1, w):
        """ calculates the utility of the bundle implied by the nested shares 
        
        Args:
            s1 (float): budget share parameter for food
            w (float): budget share parameter for transport
            
        Returns:
            u (float): total utility    
        """
        
        # i. computing the quantities
        x1, x2, x3 = self.quantities(s1, w)
        
        # j. computing return utility
        return self.utility(x1, x2, x3)