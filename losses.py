def loss_function(X, constraints, assistant_count, course_count):
    X_to_be_used = X.reshape(assistant_count, course_count)
    
    return 100 * constraints.hard_constraint_1(X_to_be_used) + 100 * constraints.hard_constraint_2(X_to_be_used) + \
                50.0 * constraints.soft_constraint_1(X_to_be_used) + \
                20.0 * constraints.soft_constraint_2(X_to_be_used) + \
                10.0 * constraints.soft_constraint_3(X_to_be_used) + \
                20.0 * constraints.soft_constraint_4(X_to_be_used)
