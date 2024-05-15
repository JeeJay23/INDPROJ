__kernel void apply_gain(__global const float* input,
                         __global float* output,
                         const float gain
                         )
{
    int gid = get_global_id(0);
    
    // Apply gain to each sample
    output[gid] = input[gid] * gain;
}
