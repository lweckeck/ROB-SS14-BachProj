

// **************************************************
// File generated by: neuroConstruct v1.5.2 
// **************************************************




// This is a GENESIS script file generated from a ChannelML v1.8.1 file
// The ChannelML file is mapped onto a tabchannel object


// Units of ChannelML file: Physiological Units, units of GENESIS file generated: SI Units

/*
    ChannelML file based on Traub et al. 2003
*/

// NOTE: There are parameters in the ChannelML file, so there will be a seperate init of the table
extern init_naf
        
    
function make_naf

        /*
            Fast Sodium transient (inactivating) current. Based on NEURON port of FRB L2/3 model from Traub et al 2003. Same channel used in Traub et al 2005

            
Reference: Roger D. Traub, Eberhard H. Buhl, Tengis Gloveli, and Miles A. Whittington                
Fast Rhythmic Bursting Can Be Induced in Layer 2/3 Cortical Neurons by Enhancing Persistent Na+ Conductance or by Blocking BK Channels
J Neurophysiol 89: 909-921, 2003
            Pubmed: http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=pubmed&dopt=Abstract&list_uids=12574468

            
Reference: Roger D. Traub, Diego Contreras, Mark O. Cunningham, Hilary Murray, Fiona E. N. LeBeau, Anita Roopun, Andrea Bibbig, W. Bryan Wilent, Michael J. Higley, and Miles A. Whittington
Single-column thalamocortical network model exhibiting gamma oscillations, sleep spindles, and epileptogenic bursts.
J. Neurophysiol. 93, 2194-2232, 2005
            Pubmed: http://www.ncbi.nlm.nih.gov/pubmed/15525801?dopt=Abstract

        */
        

        str chanpath = "/library/naf"

        if ({exists {chanpath}})
            return
        end
        
        create tabchannel {chanpath}
            

        setfield {chanpath} \ 
            Ek              0.05 \
            Ik              0  \
            Xpower          3 \
            Ypower          1
        
        setfield {chanpath} \
            Gbar 1875 \
            Gk              0 

        
        // There are parameters in the ChannelML file, which may be changed after initialisation which could mean the tables 
        // will need to be updated. Seperating out the generation of the table values into init function.
        
        
        addfield {chanpath} fastNa_shift
        setfield {chanpath} fastNa_shift 0 // Note units of this will be determined by its usage in the generic functions
        
        addfield {chanpath} a
        setfield {chanpath} a 0 // Note units of this will be determined by its usage in the generic functions
        
        addfield {chanpath} b
        setfield {chanpath} b 0 // Note units of this will be determined by its usage in the generic functions
        
        addfield {chanpath} c
        setfield {chanpath} c 0 // Note units of this will be determined by its usage in the generic functions
        
        addfield {chanpath} d
        setfield {chanpath} d 0 // Note units of this will be determined by its usage in the generic functions
        
        
        init_naf {chanpath}  // Initialisation of the tables
        
end // End of main channel definition


// calling this function after changing the extra parameters/added fields will updated the table
function init_naf(chanpath)

        str chanpath
        
        // Retrieving the param values as local variables
        
        float fastNa_shift = {getfield {chanpath} fastNa_shift}
        
        float a = {getfield {chanpath} a}
        
        float b = {getfield {chanpath} b}
        
        float c = {getfield {chanpath} c}
        
        float d = {getfield {chanpath} d}
        
        // No Q10 temperature adjustment found
        float temp_adj_m = 1
        float temp_adj_h = 1
    

        float tab_divs = 741
        float v_min = -0.12

        float v_max = 0.06

        float v, dv, i
            
        // Creating table for gate m, using name X for it here

        float dv = ({v_max} - {v_min})/{tab_divs}
            
        call {chanpath} TABCREATE X {tab_divs} {v_min} {v_max}
                
        v = {v_min}

            

        for (i = 0; i <= ({tab_divs}); i = i + 1)
            
            // Looking at rate: tau
                

            float tau
                
                        
            // Found a generic form of rate equation for tau, using expression: (v + fastNa_shift) < -30 ? 0.025 + 0.14 * ( exp ( ((v + fastNa_shift) + 30) / 10) ) : 0.02 + a + (0.145 + b) * ( exp ( -1 * ((v + fastNa_shift + d) + 30) / (10.0 + c)) )
            // Will translate this for GENESIS compatibility...
                    
            // Equation (and all ChannelML file values) in Physiological Units but this script in SI Units
            

            v = v * 1000 // temporarily set v to units of equation...
            

            if ({v + fastNa_shift} < -30 )
                tau =  0.025 + 0.14 * { exp { {{v + fastNa_shift} + 30} / 10} } 
            else
                tau =  0.02 + a + {0.145 + b} * { exp { -1 * {{v + fastNa_shift + d} + 30} / {10.0 + c}} }
            end
        
            
            v = v * 0.001 // reset v
            
            // Set correct units of tau
            tau = tau * 0.001
            // Looking at rate: inf
                

            float inf
                
                        
            // Found a generic form of rate equation for inf, using expression:  1 / ( 1 + (exp ( ( -1 * (v + fastNa_shift) - 38) / 10)) ) 
            // Will translate this for GENESIS compatibility...
                    
            // Equation (and all ChannelML file values) in Physiological Units but this script in SI Units
            

            v = v * 1000 // temporarily set v to units of equation...
            inf =  1 / { 1 + {exp { { -1 * {v + fastNa_shift} - 38} / 10}} } 
            
            v = v * 0.001 // reset v
            

            // Evaluating the tau and inf expressions

                    
            tau = tau/temp_adj_m
    

            
            // Working out the "real" alpha and beta expressions from the tau and inf
            
            float alpha
            float beta
            alpha = inf / tau   
            beta = (1- inf)/tau
            
            
            setfield {chanpath} X_A->table[{i}] {alpha}
            setfield {chanpath} X_B->table[{i}] {alpha + beta}

                
            v = v + dv

        end // end of for (i = 0; i <= ({tab_divs}); i = i + 1)
            
        setfield {chanpath} X_A->calc_mode 1 X_B->calc_mode 1
                    
        // Creating table for gate h, using name Y for it here

        float dv = ({v_max} - {v_min})/{tab_divs}
            
        call {chanpath} TABCREATE Y {tab_divs} {v_min} {v_max}
                
        v = {v_min}

            

        for (i = 0; i <= ({tab_divs}); i = i + 1)
            
            // Looking at rate: tau
                

            float tau
                
                        
            // Found a generic form of rate equation for tau, using expression: 0.15 + 1.15 / ( 1 + ( exp (( ( v + fastNa_shift * 0 ) + 37 ) / 15) ) )
            // Will translate this for GENESIS compatibility...
                    
            // Equation (and all ChannelML file values) in Physiological Units but this script in SI Units
            

            v = v * 1000 // temporarily set v to units of equation...
            tau = 0.15 + 1.15 / { 1 + { exp {{ { v + fastNa_shift * 0 } + 37 } / 15} } }
            
            v = v * 0.001 // reset v
            
            // Set correct units of tau
            tau = tau * 0.001
            // Looking at rate: inf
                

            float inf
                
                        
            // Found a generic form of rate equation for inf, using expression: 1 / ( 1 + (exp (( ( v + fastNa_shift * 0 ) + 62.9 ) / 10.7)) )
            // Will translate this for GENESIS compatibility...
                    
            // Equation (and all ChannelML file values) in Physiological Units but this script in SI Units
            

            v = v * 1000 // temporarily set v to units of equation...
            inf = 1 / { 1 + {exp {{ { v + fastNa_shift * 0 } + 62.9 } / 10.7}} }
            
            v = v * 0.001 // reset v
            

            // Evaluating the tau and inf expressions

                    
            tau = tau/temp_adj_h
    

            
            // Working out the "real" alpha and beta expressions from the tau and inf
            
            float alpha
            float beta
            alpha = inf / tau   
            beta = (1- inf)/tau
            
            
            setfield {chanpath} Y_A->table[{i}] {alpha}
            setfield {chanpath} Y_B->table[{i}] {alpha + beta}

                
            v = v + dv

        end // end of for (i = 0; i <= ({tab_divs}); i = i + 1)
            
        setfield {chanpath} Y_A->calc_mode 1 Y_B->calc_mode 1
                    


end
