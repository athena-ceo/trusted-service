package delphes;

public class Case {
	String date_demande;
	String departement;
	String date_expiration_api;
	boolean mention_de_risque_sur_l_emploi;
	
	public String getDate_demande() {
		return date_demande;
	}
	public void setDate_demande(String date_demande) {
		this.date_demande = date_demande;
	}
	public String getDepartement() {
		return departement;
	}
	public void setDepartement(String departement) {
		this.departement = departement;
	}
	public String getDate_expiration_api() {
		return date_expiration_api;
	}
	public void setDate_expiration_api(String date_expiration_api) {
		this.date_expiration_api = date_expiration_api;
	}
	public boolean isMention_de_risque_sur_l_emploi() {
		return mention_de_risque_sur_l_emploi;
	}
	public void setMention_de_risque_sur_l_emploi(boolean mention_de_risque_sur_l_emploi) {
		this.mention_de_risque_sur_l_emploi = mention_de_risque_sur_l_emploi;
	}
	
	
}
