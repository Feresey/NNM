import math

import matplotlib.pyplot as plt


class Task:
    def __init__(self, **params):
        """
        parameters:

        a_condition, b_condition, c_condition -
        callable objects to check a, b, c constants

        free_function - function in source differential task

        l0_alpha, l0_beta, l0_f -
        constants and callable object for l0 condition

        l1_alpha, l1_beta, l1_f -
        constants and callable object for l1 condition

        l1 -
        value of l1

        t_f
        constants and callable object for t condition

        f - analytical solution, callable object
        """

        class Condition:
            def __init__(self, alpha, beta, f, axis):
                self.alpha = alpha
                self.beta = beta
                self.__f_inner = f
                self.__axis = axis

            def set_constants(self, args):
                if self.__axis == 'x':
                    self.f = lambda t: self.__f_inner(t=t, a=args.get('a', 0), b=args.get('b', 0), c=args.get('c', 0))
                elif self.__axis == 't':
                    self.f = lambda x: self.__f_inner(x=x, a=args.get('a', 0), b=args.get('b', 0), c=args.get('c', 0))

        self.__conditions = {}
        if 'a_condition' in params:
            self.__conditions['a'] = params['a_condition']
        self.__a = 0

        if 'b_condition' in params:
            self.__conditions['b'] = params['b_condition']
        self.__b = 0

        if 'c_condition' in params:
            self.__conditions['c'] = params['c_condition']
        self.__c = 0

        self.__constants_set = False

        self.__free_function = params.get('free_function', lambda **args: 0)

        self.__l0_cond = Condition(
            params.get('l0_alpha', 0),
            params.get('l0_beta', 0),
            params.get('l0_f', lambda **args: 0),
            axis='x'
        )
        self.__l0 = 0
        self.__l1 = params.get('l1', 1)
        self.__l1_cond = Condition(
            params.get('l1_alpha', 0),
            params.get('l1_beta', 0),
            params.get('l1_f', lambda **args: 0),
            axis='x'
        )
        self.__t_cond = Condition(
            0,
            1,
            params.get('t_f', lambda **args: 0),
            axis='t'
        )
        self.__res_function_inner = params.get('f', lambda **args: 0)

        self.__solve_types = ['explict', 'implict', 'crank–nicolson', 'custom']
        self.__approximation_types = ['two-point first order', 'three-point second order', 'two-point second order']

    def __constant_is_correct(self, const, args):
        if const not in self.__conditions and const in args:
            print('parameter "%s" is not required and will be ignored' % (const))
            return True
        elif const in self.__conditions:
            if const in args and self.__conditions[const](args[const]):
                return True
            elif const in args:
                print('parameter "%s" is set, but not allowed by condition' % (const))
                self.__constants_set = False
                return False
            else:
                print('parameter "%s" is not set, but required' % (const))
                self.__constants_set = False
                return False
        return True

    def set_constants(self, **args):
        self.__constants_set = False

        if self.__constant_is_correct('a', args):
            self.__a = args.get('a', 0)
        else:
            return
        if self.__constant_is_correct('b', args):
            self.__b = args.get('b', 0)
        else:
            return
        if self.__constant_is_correct('c', args):
            self.__c = args.get('c', 0)
        else:
            return

        self.__res_function = lambda x, t: self.__res_function_inner(x=x, t=t, a=self.__a, b=self.__b, c=self.__c, d=self.__free_function(x=x, t=t))

        self.__l0_cond.set_constants(args)
        self.__l1_cond.set_constants(args)
        self.__t_cond.set_constants(args)

        self.__t = args.get('t', 1)

        self.__constants_set = True

    def __approximate_first_line(self, approximation_type):
        first_line_coefficients = {}

        if self.__l0_cond.alpha == 0:
            first_line_coefficients['u^k+1_0'] =\
                + self.__l0_cond.beta
            first_line_coefficients['phi^k+1'] =\
                + 1
        elif approximation_type == 'two-point first order':
            first_line_coefficients['u^k+1_0'] =\
                + self.__h * self.__l0_cond.beta\
                - self.__l0_cond.alpha
            first_line_coefficients['u^k+1_1'] =\
                + self.__l0_cond.alpha

            first_line_coefficients['phi^k+1'] =\
                + self.__h
        elif approximation_type == 'three-point second order':
            first_line_coefficients['u^k+1_0'] =\
                - 3 * self.__l0_cond.alpha\
                + 2 * self.__h * self.__l0_cond.beta
            first_line_coefficients['u^k+1_1'] =\
                + 4 * self.__l0_cond.alpha
            first_line_coefficients['u^k+1_2'] =\
                - self.__l0_cond.alpha

            first_line_coefficients['phi^k+1'] =\
                + 2 * self.__h
        elif approximation_type == 'two-point second order':
            first_line_coefficients['u^k+1_0'] =\
                + self.__schema_coefficients['u^k+1_j']\
                + self.__schema_coefficients['u^k+1_j-1'] * (
                    + 2 * self.__h * self.__l0_cond.beta / self.__l0_cond.alpha
                )
            first_line_coefficients['u^k+1_1'] =\
                + self.__schema_coefficients['u^k+1_j+1']\
                + self.__schema_coefficients['u^k+1_j-1']
            first_line_coefficients['phi^k+1'] =\
                + self.__schema_coefficients['u^k+1_j-1'] * (
                    + 2 * self.__h / self.__l0_cond.alpha
                )

            first_line_coefficients['u^k_0'] =\
                + self.__schema_coefficients['u^k_j']\
                + self.__schema_coefficients['u^k_j-1'] * (
                    + 2 * self.__h * self.__l0_cond.beta / self.__l0_cond.alpha
                )
            first_line_coefficients['u^k_1'] =\
                + self.__schema_coefficients['u^k_j+1']\
                + self.__schema_coefficients['u^k_j-1']
            first_line_coefficients['phi^k'] =\
                + self.__schema_coefficients['u^k_j-1'] * (
                    - 2 * self.__h / self.__l0_cond.alpha
                )

        self.__first_coefficients = [
            first_line_coefficients.get('u^k+1_2', 0),
            first_line_coefficients.get('u^k+1_0', 0),
            first_line_coefficients.get('u^k+1_1', 0),
            lambda u1, u2, x, t:
                + first_line_coefficients.get('u^k_0', 0) * u1
                + first_line_coefficients.get('u^k_1', 0) * u2
                + first_line_coefficients.get('phi^k+1', 0) * self.__l0_cond.f(t)
                + first_line_coefficients.get('phi^k', 0) * self.__l0_cond.f(t - self.__tau)
                + self.__schema_coefficients['f^k+1'] * self.__free_function(x=x, t=t)
                + self.__schema_coefficients['f^k'] * self.__free_function(x=x, t=t - self.__tau)
        ]

    def __approximate_last_line(self, approximation_type):
        last_line_coefficients = {}

        if self.__l1_cond.alpha == 0:
            last_line_coefficients['u^k+1_n'] =\
                + self.__l1_cond.beta
            last_line_coefficients['phi^k+1'] =\
                + 1
        elif approximation_type == 'two-point first order':
            last_line_coefficients['u^k+1_n-1'] =\
                - self.__l1_cond.alpha
            last_line_coefficients['u^k+1_n'] =\
                + self.__l1_cond.alpha\
                + self.__h * self.__l1_cond.beta

            last_line_coefficients['phi^k+1'] =\
                + self.__h
        elif approximation_type == 'three-point second order':
            last_line_coefficients['u^k+1_n-2'] =\
                + self.__l1_cond.alpha
            last_line_coefficients['u^k+1_n-1'] =\
                - 4 * self.__l1_cond.alpha
            last_line_coefficients['u^k+1_n'] =\
                + 3 * self.__l1_cond.alpha\
                + 2 * self.__h * self.__l1_cond.beta

            last_line_coefficients['phi^k+1'] =\
                + 2 * self.__h
        elif approximation_type == 'two-point second order':
            last_line_coefficients['u^k+1_n-1'] =\
                + self.__schema_coefficients['u^k+1_j-1']\
                + self.__schema_coefficients['u^k+1_j+1']
            last_line_coefficients['u^k+1_n'] =\
                + self.__schema_coefficients['u^k+1_j']\
                + self.__schema_coefficients['u^k+1_j+1'] * (
                    - 2 * self.__h * self.__l1_cond.beta / self.__l1_cond.alpha
                )
            last_line_coefficients['phi^k+1'] =\
                + self.__schema_coefficients['u^k+1_j+1'] * (
                    - 2 * self.__h / self.__l1_cond.alpha
                )

            last_line_coefficients['u^k_n-1'] =\
                + self.__schema_coefficients['u^k_j-1']\
                + self.__schema_coefficients['u^k_j+1']
            last_line_coefficients['u^k_n'] =\
                + self.__schema_coefficients['u^k_j']\
                + self.__schema_coefficients['u^k_j+1'] * (
                    - 2 * self.__h * self.__l1_cond.beta / self.__l1_cond.alpha
                )
            last_line_coefficients['phi^k'] =\
                + self.__schema_coefficients['u^k_j+1'] * (
                    + 2 * self.__h / self.__l1_cond.alpha
                )

        self.__last_coefficients = [
            last_line_coefficients.get('u^k+1_n-1', 0),
            last_line_coefficients.get('u^k+1_n', 0),
            last_line_coefficients.get('u^k+1_n-2', 0),
            lambda u1, u2, x, t:
                + last_line_coefficients.get('u^k_n-1', 0) * u1
                + last_line_coefficients.get('u^k_n', 0) * u2
                + last_line_coefficients.get('phi^k+1', 0) * self.__l1_cond.f(t)
                + last_line_coefficients.get('phi^k', 0) * self.__l1_cond.f(t - self.__tau)
                + self.__schema_coefficients['f^k+1'] * self.__free_function(x=x, t=t)
                + self.__schema_coefficients['f^k'] * self.__free_function(x=x, t=t - self.__tau)
        ]

    def __make_coefficients_matrix(self, approximation_type):
        self.__schema_coefficients = {
            'u^k+1_j-1':
                - 2 * self.__tau * self.__theta * self.__a
                + self.__h * self.__tau * self.__theta * self.__b,
            'u^k+1_j':
                + 2 * self.__h ** 2
                + 4 * self.__tau * self.__theta * self.__a
                - 2 * self.__h ** 2 * self.__tau * self.__theta * self.__c,
            'u^k+1_j+1':
                - 2 * self.__tau * self.__theta * self.__a
                - self.__h * self.__tau * self.__theta * self.__b,
            'f^k+1':
                + 2 * self.__h ** 2 * self.__tau * self.__theta,

            'u^k_j-1':
                + 2 * self.__tau * (1 - self.__theta) * self.__a
                - self.__h * self.__tau * (1 - self.__theta) * self.__b,
            'u^k_j':
                + 2 * self.__h ** 2
                - 4 * self.__tau * (1 - self.__theta) * self.__a
                + 2 * self.__h ** 2 * self.__tau * (1 - self.__theta) * self.__c,
            'u^k_j+1':
                + 2 * self.__tau * (1 - self.__theta) * self.__a
                + self.__h * self.__tau * (1 - self.__theta) * self.__b,
            'f^k':
                + 2 * self.__h ** 2 * self.__tau * (1 - self.__theta),
        }

        self.__approximate_first_line(approximation_type)

        self.__inner_coefficients = [
            self.__schema_coefficients['u^k+1_j-1'],
            self.__schema_coefficients['u^k+1_j'],
            self.__schema_coefficients['u^k+1_j+1'],
            lambda u1, u2, u3, x, t:
                + self.__schema_coefficients['u^k_j-1'] * u1
                + self.__schema_coefficients['u^k_j'] * u2
                + self.__schema_coefficients['u^k_j+1'] * u3
                + self.__schema_coefficients['f^k+1'] * self.__free_function(x=x, t=t)
                + self.__schema_coefficients['f^k'] * self.__free_function(x=x, t=t - self.__tau)
        ]

        self.__approximate_last_line(approximation_type)


    def __prepare_to_run_trough(self, coefs):
        if coefs[0][0] != 0:
            if coefs[1][2] != 0:
                k = coefs[0][0] / coefs[1][2]
                coefs[0][0] = 0
                coefs[0][1] -= coefs[1][0] * k
                coefs[0][2] -= coefs[1][1] * k
                coefs[0][-1] -= coefs[1][-1] * k
            else:
                k = coefs[0][0] / coefs[2][1]
                coefs[0][0] = 0
                coefs[0][2] -= coefs[2][0] * k
                coefs[0][-1] -= coefs[2][-1] * k

        if coefs[-1][2] != 0:
            if coefs[-2][0] != 0:
                k = coefs[-1][2] / coefs[-2][0]
                coefs[-1][2] = 0
                coefs[-1][1] -= coefs[-2][2] * k
                coefs[-1][0] -= coefs[-2][1] * k
                coefs[-1][-1] -= coefs[-2][-1] * k
            else:
                k = coefs[-1][2] / coefs[-3][1]
                coefs[-1][2] = 0
                coefs[-1][0] -= coefs[-3][2] * k
                coefs[-1][-1] -= coefs[-3][-1] * k

    def __diagonal_predominance(self, coefs):
        has_strong = False
        for line in coefs:
            if abs(line[1]) < abs(line[0]) + abs(line[2]):
                return False
            if abs(line[1]) > abs(line[0]) + abs(line[2]):
                has_strong = True
        return has_strong

    def __run_through(self, coefs):
        for line_ind in range(1, self.__n):
            k = coefs[line_ind][0] / coefs[line_ind - 1][1]
            coefs[line_ind][0] = 0
            coefs[line_ind][1] -= k * coefs[line_ind - 1][2]
            coefs[line_ind][-1] -= k * coefs[line_ind - 1][-1]

        for line_ind in range(self.__n - 2, -1, -1):
            k = coefs[line_ind][2] / coefs[line_ind + 1][1]
            coefs[line_ind][2] = 0
            coefs[line_ind][-1] -= k * coefs[line_ind + 1][-1]

        for line_ind in range(self.__n):
            coefs[line_ind][-1] /= coefs[line_ind][1]
            coefs[line_ind][1] = 1

    def solve(self, solve_type=None, approximation_type=None, k=None, n=None, courant=0.5, theta=None):
        if not self.__constants_set:
            print('constants in the task are not set')
            return None, None, None

        if solve_type not in self.__solve_types:
            print('incorrect solve type, allowed types are: %s' % ', '.join(self.__solve_types))
            return None, None, None

        if approximation_type not in self.__approximation_types:
            print('incorrect approximation type, allowed types are: %s' % ', '.join(self.__approximation_types))
            return None, None, None

        if solve_type == 'explict':
            self.__theta = 0.0
        elif solve_type == 'implict':
            self.__theta = 1.0
        elif solve_type == 'crank–nicolson':
            self.__theta = 0.5
        elif solve_type == 'custom':
            if theta is None:
                print('custom solve type was selected, but parameter "theta" was not set')
                return None, None, None
            self.__theta = theta

        if solve_type != 'custom' and theta is not None:
            print('solve type is not "custom", so value of parameter "theta" will be ignored')

        if n is None and k is None:
            print('either n or k must be set')
            return None, None, None
        elif k is None:
            self.__h = 1.0 * (self.__l1 - self.__l0) / (n - 1)
            self.__tau = self.__h ** 2 / self.__a * courant
        elif n is None:
            self.__tau = 1.0 * self.__t / (k - 1)
            self.__h = math.sqrt(self.__tau * self.__a / courant)
        else:
            self.__h = 1.0 * (self.__l1 - self.__l0) / (n - 1)
            self.__tau = 1.0 * self.__t / (k - 1)
            if self.__a * self.__tau / self.__h ** 2 > courant:
                print('tau and h must satisfy Courant condition')
                print('resolved {} instead of {}'.format(self.__a * self.__tau / self.__h ** 2, courant))

        self.__n = n if n is not None else int(1.0 * (self.__l1 - self.__l0) / self.__h + 1)
        self.__k = k if k is not None else int(1.0 * self.__t / self.__tau + 1)

        self.__make_coefficients_matrix(approximation_type)

        res = []
        pillar_line = [self.__t_cond.f(self.__l0 + self.__h * i) for i in range(self.__n)]
        res.append([self.__t_cond.f(self.__l0 + self.__h * i) for i in range(self.__n)])

        for tk in range(1, self.__k):
            coefs = [
                [coef for coef in self.__first_coefficients[:-1]] +
                [self.__first_coefficients[-1](pillar_line[0], pillar_line[1], self.__l0, tk * self.__tau)]
            ] + [
                [coef for coef in self.__inner_coefficients[:-1]] +
                [self.__inner_coefficients[-1](pillar_line[i - 1], pillar_line[i], pillar_line[i + 1], self.__l0 + i * self.__h, tk * self.__tau)]
                for i in range(1, self.__n - 1)
            ] + [
                [coef for coef in self.__last_coefficients[:-1]] +
                [self.__last_coefficients[-1](pillar_line[-2], pillar_line[-1], self.__l1, tk * self.__tau)]
            ]

            self.__prepare_to_run_trough(coefs)
            self.__run_through(coefs)

            pillar_line = [coefs[i][-1] for i in range(self.__n)]
            res.append([coefs[i][-1] for i in range(self.__n)])

        sample = [[self.__res_function(self.__l0 + self.__h * dx, self.__tau * dt) for dx in range(self.__n)] for dt in range(self.__k)]
        errors = [[sample[i][j] - res[i][j] for j in range(self.__n)] for i in range(self.__k)]

        return res, sample, errors

    # def solve_function_plot_interractor(self, solve, theta, approximation_type, n, k, courant, direction, slice_rate, policy):
    #     plt.figure(figsize=(15, 10))

    #     if solve == 'explict':
    #         theta = 0.0
    #     elif solve == 'implict':
    #         theta = 1.0
    #     elif solve == 'crank–nicolson':
    #         theta = 0.5

    #     res, sample, _ = self.solve(
    #         solve_type='custom',
    #         approximation_type=approximation_type,
    #         k=(k if policy != 'n' else None),
    #         n=(n if policy != 'k' else None),
    #         courant=courant,
    #         theta=theta
    #     )

    #     if direction == 'x':
    #         t = [self.__tau * i for i in range(self.__k)]
    #         slice_ind = int((self.__l1 - self.__l0) * slice_rate / self.__h)
    #         plt.plot(
    #             t,
    #             [line[slice_ind] for line in sample],
    #             label='sample'
    #         )
    #         plt.plot(
    #             t,
    #             [line[slice_ind] for line in res],
    #             label='calculated'
    #         )
    #         plt.xlabel('t')
    #     if direction == 't':
    #         x = [self.__h * i for i in range(self.__n)]
    #         slice_ind = int(self.__t * slice_rate / self.__tau)
    #         plt.plot(
    #             x,
    #             sample[slice_ind],
    #             label='sample'
    #         )
    #         plt.plot(
    #             x,
    #             res[slice_ind],
    #             label='calculated'
    #         )
    #         plt.xlabel('x')

    #     plt.ylabel("value")
    #     plt.legend()
    #     plt.grid()

    # def solve_error_plot_interractor(self, solve, theta, approximation_type, n, k, courant, direction, slice_rate, policy):
    #     plt.figure(figsize=(15, 10))

    #     if solve == 'explict':
    #         theta = 0.0
    #     elif solve == 'implict':
    #         theta = 1.0
    #     elif solve == 'crank–nicolson':
    #         theta = 0.5

    #     _, _, error = self.solve(
    #         solve_type='custom',
    #         approximation_type=approximation_type,
    #         k=(k if policy != 'n' else None),
    #         n=(n if policy != 'k' else None),
    #         courant=courant,
    #         theta=theta
    #     )

    #     if direction == 'x':
    #         t = [self.__tau * i for i in range(self.__k)]
    #         slice_ind = int((self.__l1 - self.__l0) * slice_rate / self.__h)
    #         plt.plot(
    #             t,
    #             [line[slice_ind] for line in error]
    #         )
    #         plt.xlabel('t')
    #     if direction == 't':
    #         x = [self.__h * i for i in range(self.__n)]
    #         slice_ind = int(self.__t * slice_rate / self.__tau)
    #         plt.plot(
    #             x,
    #             error[slice_ind]
    #         )
    #         plt.xlabel('x')

    #     plt.ylabel("error")
    #     plt.grid()

    # def solve_error_aggregate_plot_interractor(self, solve, theta, approximation_type, n, k, courant, policy):
    #     plt.figure(figsize=(15, 10))

    #     if solve == 'explict':
    #         theta = 0.0
    #     elif solve == 'implict':
    #         theta = 1.0
    #     elif solve == 'crank–nicolson':
    #         theta = 0.5

    #     _, _, error = self.solve(
    #         solve_type='custom',
    #         approximation_type=approximation_type,
    #         k=(k if policy != 'n' else None),
    #         n=(n if policy != 'k' else None),
    #         courant=courant,
    #         theta=theta
    #     )

    #     t = [self.__tau * i for i in range(self.__k)]
    #     plt.plot(
    #         t,
    #         [max([abs(el) for el in line]) for line in error]
    #     )
    #     plt.xlabel('t')

    #     plt.ylabel("error")
    #     plt.grid()

    def calc_all_solves(self, policy, l_border, r_border, step):
        errors = {}

        for solve in self.__solve_types:
            for approx in self.__approximation_types:
                errors[' '.join([solve, approx])] = []

        steps = []
        for i in range(l_border, r_border, step):
            steps.append((self.l() if policy == 'n' else self.t()) / i)
            for solve in self.__solve_types:
                if solve == 'custom':
                    continue
                for approx in self.__approximation_types:
                    _, _, err = self.solve(
                        solve_type=solve,
                        approximation_type=approx,
                        k=(i if policy != 'n' else None),
                        n=(i if policy != 'k' else None)
                    )
                    merr = 0
                    for line in err:
                        for el in line:
                            merr = max(abs(el), abs(merr))
                    errors[' '.join([solve, approx])].append(merr)
        return steps, errors

    def l(self):
        return self.__l1 - self.__l0

    def t(self):
        return self.__t
