# Responders

Task-specific simulation responders/samplers live here.

- `TaskSamplerResponder` handles both scripted and sampled temporal-bisection simulation modes.
- Scripted sim uses `config/config_scripted_sim.yaml`.
- Sampler sim uses `config/config_sampler_sim.yaml` and points to `responders.task_sampler:TaskSamplerResponder`.
