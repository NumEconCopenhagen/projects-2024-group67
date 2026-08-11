# Constructing the life cycle model: 
import numpy as np

# The life cycle model is constructed based on the framework introduced in the lecture: 
class life_cycle_model:
    """Specifying the framework of the Life cycle income model"""

    def __init__(self, **kwargs):
        """Specifying the defualt parameters. These can be overwritten by specifying other arguments"""

        # Specifying the baseline structure: 
        self.N = 50_000
        self.age_start = 18
        self.age_retire = 65
        self.seed = 2026

        # Education: Index 0 = short, Index 1 = medium, Index 2 = long. 
        self.pe = np.array([0.40, 0.35, 0.25])  # the different education probabilities
        self.se = np.array([1, 3, 5])           # years of education
        self.he0 = np.array([1.00, 1.20, 1.55]) # the initial levels of human capital
        self.delta_e = np.array([0.010, 0.020, 0.030]) # growth of human capital

        # labour market: 
        self.lam = 0.50 # job finding probability
        self.sigma = 0.05   # job seperation probability

        # human capital: 
        self.delta = 0.06     # depreciation while unemployed
        self.sigma_psi = 0.10 # std. of shock

        # income: 
        self.y_SU = 0.45  # student grant
        self.rho = 0.60   # replacement rate
        self.floor = 0.35 # benefit floor when never employed

        # overriding default settings with keyword arguments: 
        for key, value in kwargs.items(): 
            setattr(self, key, value)

        # Deriving the number of ages:
        self.T = self.age_retire - self.age_start

        # constructing the pseudo RNG: 
        self.rng = np.random.default_rng(self.seed)

    def sim_life_cycle_model(self):
        """ Simulating the model and storing income, status and eduaction in attributes in the class"""

        # Education is drawn at the age of 18: 
        education = self.rng.choice(3, size = self.N, p = self.pe)
        years_edu = self.se[education]  # the number of years each person spends in education
        h_start = self.he0[education]   # initial levels of human capital
        growth = self.delta_e[education] # growth of human capital

        # listing the state variables: 
        h = np.zeros(self.N)                # current human capital
        employed = np.zeros(self.N, bool)   # employed at the age
        has_worked = np.zeros(self.N, bool) # dummy for whether the person has ever been employed
        last_income = np.zeros(self.N)

        # results: 
        income = np.zeros((self.N, self.T)) 
        status = np.zeros((self.N, self.T), int)

        # looping over the ages for which a person is eligble for work: 
        for t in range(self.T):

            in_school = t < years_edu     # still at school
            in_labor = t >= years_edu     # labor market eligible

            # people who just finished school enter the labour market unemployed
            entering = t == years_edu
            h[entering] = h_start[entering]
            employed[entering] = False

            # constructing the framework for income:
            y = np.full(self.N, self.y_SU)                       # income for students are the student grant
            y[in_labor & employed] = h[in_labor & employed]      # income for employed are their own human capital
            unemployed = in_labor & ~employed
            y[unemployed] = self.rho * last_income[unemployed]   # income for unemployed are the replacement rate
            y[unemployed & ~has_worked] = self.floor             # income for those who have never worked gets the UI benefit
            income[:, t] = y

            # Status for the latest job income:
            status[in_school, t] = -1
            status[unemployed, t] = 0
            status[in_labor & employed, t] = 1
            last_income[in_labor & employed] = h[in_labor & employed]
            has_worked[in_labor & employed] = True
            
            if t < self.T - 1:   # update state for the next age

                # the human capital increases for those employed and decreases for those unemployed:
                psi = self.rng.lognormal(-0.5 * self.sigma_psi**2, self.sigma_psi, size=self.N)
                change = np.where(employed, 1 + growth, 1 - self.delta)
                h = np.where(in_labor, h * change * psi, h)       # unchanged while studying

                # Using the RNG to construct the two stage markov chain:
                u = self.rng.random(self.N)
                finds_job = in_labor & ~employed & (u < self.lam)
                loses_job = in_labor & employed & (u < self.sigma)
                employed[finds_job] = True
                employed[loses_job] = False

        # store results
        self.education = education
        self.income = income
        self.status = status
        return self




