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

// dft assumes imaginary component of the input is 0
__kernel void dft(__global const float* input,
                  __global float* output,
                  const int N,
                  const int sign
                  )
{
    // gid is k here, representing the index on the frequency domain
    int gid = get_global_id(0);

    if (gid >= N)
        return;

    float2 sum = (float2)(0.0f, 0.0f);
    // apply dft or idft
    float omega_k = (-2 * sign * gid) * M_PI / (float)N;
    for (int n = 0; n < N; n++)
    {
        float x = input[n];
        // sincos could be faster
        float2 s = (float2)(x*cos(omega_k * n), x*-sin(omega_k * n));
        sum += s;
    }

    if (sign == 1){
        // calculate abs and return it
        output[gid] = sqrt(sum.x * sum.x + sum.y * sum.y);
    }
    else {
        // idft not implemented
        // output[gid] = sum / (float)N;
    }
}

// kernel from https://ochafik.com/p_501, used as a reference
__kernel void dft2(
	__global const double2 *in, // complex values input
	__global double2 *out,      // complex values output
	int length,                 // number of input and output values
	int sign)                   // sign modifier in the exponential :
	                            // 1 for forward transform, -1 for backward.
{
	// Get the varying parameter of the parallel execution :
	int i = get_global_id(0);
	
	// In case we're executed "too much", check bounds :
	if (i >= length)
		return;
	
	// Initialize sum and inner arguments
	double2 tot = 0;
	double param = (-2 * sign * i) * M_PI / (double)length;
	
	for (int k = 0; k < length; k++) {
		double2 value = in[k];
		
		// Compute sin and cos in a single call : 
		double c;
		double s = sincos(k * param, &c);
		
		// This adds (value.x * c - value.y * s, value.x * s + value.y * c) to the sum :
		tot += (double2)(
			dot(value, (double2)(c, -s)), 
			dot(value, (double2)(s, c))
		);
	}
	
	if (sign == 1) {
		// forward transform (space -> frequential)
		out[i] = tot;
	} else {
		// backward transform (frequential -> space)
		out[i] = tot / (double)length;
	}
}
