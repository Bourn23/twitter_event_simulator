import matplotlib.pyplot as plt
import numpy as np
import math
import bisect

# Define the configurations
class Config:
    def __init__(self, constant=None, piecewise_constant=None, linear_ramp_to_constant=None, linear_ramp_to_cosine=None):
        self.constant = constant
        self.piecewise_constant = piecewise_constant
        self.linear_ramp_to_constant = linear_ramp_to_constant
        self.linear_ramp_to_cosine = linear_ramp_to_cosine

# Piecewise constant configuration
class PiecewiseConstantConfig:
    def __init__(self, learning_rate_boundaries, learning_rate_values):
        self.learning_rate_boundaries = learning_rate_boundaries
        self.learning_rate_values = learning_rate_values

# Linear ramp to constant configuration
class LinearRampToConstantConfig:
    def __init__(self, learning_rate, num_ramp_steps):
        self.learning_rate = learning_rate
        self.num_ramp_steps = num_ramp_steps

# Linear ramp to cosine configuration
class LinearRampToCosineConfig:
    def __init__(self, learning_rate, final_learning_rate, num_ramp_steps, final_num_steps):
        self.learning_rate = learning_rate
        self.final_learning_rate = final_learning_rate
        self.num_ramp_steps = num_ramp_steps
        self.final_num_steps = final_num_steps

def compute_lr(lr_config, step):
    """Compute a learning rate."""
    if lr_config.constant is not None:
        return lr_config.constant
    elif lr_config.piecewise_constant is not None:
        return lr_config.piecewise_constant.learning_rate_values[
            bisect.bisect_right(lr_config.piecewise_constant.learning_rate_boundaries, step)
        ]
    elif lr_config.linear_ramp_to_constant is not None:
        slope = (
            lr_config.linear_ramp_to_constant.learning_rate
            / lr_config.linear_ramp_to_constant.num_ramp_steps
        )
        return min(lr_config.linear_ramp_to_constant.learning_rate, slope * step)
    elif lr_config.linear_ramp_to_cosine is not None:
        cfg = lr_config.linear_ramp_to_cosine
        if step < cfg.num_ramp_steps:
            slope = cfg.learning_rate / cfg.num_ramp_steps
            return slope * step
        elif step <= cfg.final_num_steps:
            return cfg.final_learning_rate + (cfg.learning_rate - cfg.final_learning_rate) * 0.5 * (
                1.0
                + math.cos(
                    math.pi * (step - cfg.num_ramp_steps) / (cfg.final_num_steps - cfg.num_ramp_steps)
                )
            )
        else:
            return cfg.final_learning_rate
    else:
        raise ValueError(f"No option selected in lr_config, passed {lr_config}")

# Configurations for visualization
steps = np.arange(0, 100)
constant_config = Config(constant=0.1)
piecewise_config = Config(piecewise_constant=PiecewiseConstantConfig([30, 60], [0.1, 0.01, 0.001]))
linear_ramp_to_constant_config = Config(linear_ramp_to_constant=LinearRampToConstantConfig(learning_rate=0.1, num_ramp_steps=50))
linear_ramp_to_cosine_config = Config(linear_ramp_to_cosine=LinearRampToCosineConfig(learning_rate=0.1, final_learning_rate=0.001, num_ramp_steps=50, final_num_steps=100))

# Compute learning rates for each step
lr_constant = [compute_lr(constant_config, step) for step in steps]
lr_piecewise = [compute_lr(piecewise_config, step) for step in steps]
lr_linear_ramp_to_constant = [compute_lr(linear_ramp_to_constant_config, step) for step in steps]
lr_linear_ramp_to_cosine = [compute_lr(linear_ramp_to_cosine_config, step) for step in steps]

# Plotting
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.plot(steps, lr_constant, label='Constant')
plt.title('Constant Learning Rate')
plt.xlabel('Steps')
plt.ylabel('Learning Rate')

plt.subplot(2, 2, 2)
plt.plot(steps, lr_piecewise, label='Piecewise Constant')
plt.title('Piecewise Constant Learning Rate')
plt.xlabel('Steps')
plt.ylabel('Learning Rate')

plt.subplot(2, 2, 3)
plt.plot(steps, lr_linear_ramp_to_constant, label='Linear Ramp to Constant')
plt.title('Linear Ramp to Constant Learning Rate')
plt.xlabel('Steps')
plt.ylabel('Learning Rate')

plt.subplot(2, 2, 4)
plt.plot(steps, lr_linear_ramp_to_cosine, label='Linear Ramp to Cosine')
plt.title('Linear Ramp to Cosine Learning Rate')
plt.xlabel('Steps')
plt.ylabel('Learning Rate')

plt.tight_layout()
plt.show()