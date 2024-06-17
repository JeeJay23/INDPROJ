__kernel void apply_gain(__global const float* input,
                         __global float* output,
                         const float gain
                         )
{
    int gid = get_global_id(0);
    
    // Apply gain to each sample
    output[gid] = input[gid] * gain;
}

__kernel void apply_convolution(__global const float* input,
                                __global const float* coefs,
                                __global float* output,
                                const int coefs_size,
                                const int input_size
                                )
{
    int gid = get_global_id(0);
    
    // Apply convolution to each sample
    float sum = 0.0f;
    for (int i = 0; i < coefs_size; i++)
    {
        if (gid + i < input_size){
            sum += input[gid + i] * coefs[i];
        }
    }
    output[gid] = sum;
}
