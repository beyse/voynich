"""Readable names for the 40 phenotype statistics (shared by figures and tables)."""
STAT = {
    'hapax': 'hapax share', 'ttr': 'type-token ratio', 'zipf': 'Zipf slope', 'wlen': 'mean word length',
    'edge_mi': 'boundary MI', 'token_mi': 'word-pair MI', 'd2_mi': 'distance-2 word MI', 'break_mi': 'line-break word MI',
    'break_edge': 'line-break boundary MI', 'adj_edge_same_n': 'boundary MI, equal n', 'space_gain': 'space predictability',
    'lex_real': 'lexicon test, real words', 'lex_synth': 'lexicon test, synthetic words', 'h2': 'conditional entropy h2',
    'h3': 'conditional entropy h3', 'h4': 'conditional entropy h4', 'lzma': 'lzma bits per character', 'page_mi': 'page MI',
    'T1_R': 'T1 line-break ratio', 'T2a_margin': 'T2a final form, margin', 'T2a_para': 'T2a final form, paragraph end',
    'T2b_T': 'T2b line-fill slack', 'T2c_ratio': 'T2c dittography', 'T3a_rho': 'T3a zero replication',
    'T3b_cons': 'T3b slot consistency', 'T3b_mono': 'T3b monotone share', 'T3c_e1': 'T3c final-position entropy',
    'T3c_s1': 'T3c initial-position entropy', 'T4_peak': 'T4 periodicity', 'T5_S': 'T5 drift shape',
    'T6a_near': 'T6a recency, near repeats', 'T6a_exact': 'T6a recency, exact repeats', 'T6b_slope': 'T6b within-page drift',
    'T7b_rate': 'T7b deviant rate', 'T7b_rec': 'T7b deviant recurrence', 'T7b_slip': 'T7b slip share',
    'E1_LSg': 'E1 line step', 'E1_PS': 'E1 paragraph step', 'E1_WLDg': 'E1 within-line decay', 'E1_WPD': 'E1 within-paragraph decay',
}
FITTED = {'T6a_near', 'T6a_exact', 'T7b_rate', 'T7b_rec', 'page_mi', 'hapax', 'ttr', 'T6b_slope', 'T3a_rho'}
