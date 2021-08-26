import requests
import shutil
import os

url_dataset='https://cbioportal-datahub.s3.amazonaws.com/' # insert the latest location of cbioportal archive here. This link was true in Feb 2021

# DOWNLOAD  Raw genomic study data from cbioportal

list_study_dirs=['acbc_mskcc_2015','acc_tcga_pan_can_atlas_2018','acyc_mda_2015','acyc_mskcc_2013','acyc_sanger_2013','all_stjude_2013','all_stjude_2015','all_stjude_2016','aml_target_2018_pub','angs_project_painter_2018','bfn_duke_nus_2015','blca_bgi','blca_cornell_2016','blca_dfarber_mskcc_2014','blca_tcga_pub_2017','brca_bccrc','brca_broad','brca_igr_2015','brca_mbcproject_wagle_2017','brca_sanger','brca_tcga_pan_can_atlas_2018','ccrcc_irc_2014','ccrcc_utokyo_2013','cesc_tcga_pan_can_atlas_2018','chol_jhu_2013','chol_nccs_2013','chol_tcga_pan_can_atlas_2018','cll_iuopa_2015','cllsll_icgc_2011','coadread_dfci_2016','coadread_genentech','coadread_tcga_pan_can_atlas_2018','ctcl_columbia_2015','desm_broad_2015','dlbc_broad_2012','dlbc_tcga_pan_can_atlas_2018','dlbcl_dfci_2018','dlbcl_duke_2017','egc_tmucih_2015','es_dfarber_broad_2014','es_iocurie_2014','esca_tcga_pan_can_atlas_2018','escc_icgc','escc_ucla_2014','gbc_shanghai_2014','gbm_tcga_pan_can_atlas_2018','hcc_inserm_fr_2015','hnsc_broad','hnsc_jhu','hnsc_mdanderson_2013','hnsc_tcga_pan_can_atlas_2018','kich_tcga_pan_can_atlas_2018','kirc_bgi','kirc_tcga_pan_can_atlas_2018','kirp_tcga_pan_can_atlas_2018','laml_tcga_pan_can_atlas_2018','lcll_broad_2013','lgg_ucsf_2014','lgggbm_tcga_pub','lihc_amc_prv','lihc_riken','lihc_tcga_pan_can_atlas_2018','luad_broad','luad_mskcc_2015','luad_tcga_pan_can_atlas_2018','lusc_tcga_pan_can_atlas_2018','mbl_broad_2012','mbl_icgc','mbl_pcgp','mbl_sickkids_2016','mcl_idibips_2013','mds_tokyo_2011','mel_tsam_liang_2017','meso_tcga_pan_can_atlas_2018','mm_broad','mpnst_mskcc','mrt_bcgsc_2016','nbl_amc_2012','nbl_broad_2013','nbl_target_2018_pub','nbl_ucologne_2015','nccrcc_genentech_2014','nepc_wcm_2016','nhl_bcgsc_2011','nhl_bcgsc_2013','npc_nusingapore','nsclc_tcga_broad_2016','ov_tcga_pan_can_atlas_2018','paac_jhu_2014','paad_icgc','paad_qcmg_uq_2016','paad_tcga_pan_can_atlas_2018','paad_utsw_2015','panet_arcnet_2017','panet_jhu_2011','panet_shanghai_2013','past_dkfz_heidelberg_2013','pcnsl_mayo_2015','pcpg_tcga_pan_can_atlas_2018','plmeso_nyu_2015','prad_broad','prad_broad_2013','prad_cpcg_2017','prad_eururol_2017','prad_fhcrc','prad_mich','prad_p1000','prad_su2c_2015','prad_tcga_pan_can_atlas_2018','rms_nih_2014','rt_target_2018_pub','sarc_tcga_pan_can_atlas_2018','sclc_cancercell_gardner_2017','sclc_clcgp','sclc_jhu','sclc_ucologne_2015','skcm_broad','skcm_broad_brafresist_2012','skcm_broad_dfarber','skcm_tcga_pan_can_atlas_2018','mel_ucla_2016','skcm_yale','stad_pfizer_uhongkong','stad_tcga_pan_can_atlas_2018','stad_uhongkong','stad_utokyo','stes_tcga_pub','tet_nci_2014','tgct_tcga_pan_can_atlas_2018','thca_tcga_pan_can_atlas_2018','thym_tcga_pan_can_atlas_2018','uccc_nih_2017','ucec_tcga_pan_can_atlas_2018','ucs_jhu_2014','ucs_tcga_pan_can_atlas_2018','um_qimr_2016','uvm_tcga_pan_can_atlas_2018','vsc_cuk_2018','wt_target_2018_pub']
urllist=[url_dataset+istudy+'.tar.gz' for istudy in list_study_dirs]

for url in urllist:
	if not os.path.exists(url.split('/')[-1]):
		r=requests.get(url,allow_redirects=True)
		open(url.split('/')[-1],'wb').write(r.content)

# Unpack Raw Study Data

flist=[fname for fname in os.listdir() if 'tar.gz' in fname]
for fname in flist:
	if not os.path.exists(fname.replace('.tar.gz','')):
		shutil.unpack_archive(fname)
		os.remove(fname)

# revert name of mel_ucla_2016 study to be compatible with clinical folder
if os.path.exists('mel_ucla_2016'):
	os.rename('mel_ucla_2016','skcm_ucla_2016')