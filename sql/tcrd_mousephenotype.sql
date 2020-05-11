-- nh = non-human
SELECT 
        COUNT(DISTINCT ph.nhprotein_id) AS mouse_protein_ids, 
        COUNT(DISTINCT ph.term_id) AS mp_term_ids, 
        COUNT(DISTINCT ph.term_name) AS mp_term_names, 
        COUNT(DISTINCT ph.procedure_name) AS mp_procedure_names, 
        COUNT(DISTINCT ph.parameter_name) AS mp_param_names, 
        ph.gp_assoc AS association 
FROM
        phenotype ph
WHERE
        ptype = 'IMPC'
GROUP BY
        association
;