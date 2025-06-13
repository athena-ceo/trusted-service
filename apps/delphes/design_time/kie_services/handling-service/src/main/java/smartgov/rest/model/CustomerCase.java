package smartgov.rest.model;

import java.time.LocalDate;
import com.fasterxml.jackson.annotation.JsonProperty;

public class CustomerCase {

    private LocalDate date_demande;
    private LocalDate date_expiration_api;
    private String departement;
    private boolean refugie_ou_protege_subsidiaire;
    private boolean risque_sur_l_emploi;

    public void setDateDemande(LocalDate d) { this.date_demande = d; }
    public void setDateExpirationApi(LocalDate d) { this.date_expiration_api = d; }
    public void setDepartement(String d) { this.departement = d; }
    public void setRefugie(boolean r) { this.refugie_ou_protege_subsidiaire = r; }
    public void setRisqueEmploi(boolean r) { this.risque_sur_l_emploi = r; } 

    @JsonProperty("date_demande")
    @org.kie.dmn.feel.lang.FEELProperty("date_demande")
    public LocalDate getDateDemande() { return this.date_demande; }

    @JsonProperty("date_expiration_api")
    @org.kie.dmn.feel.lang.FEELProperty("date_expiration_api")
    public LocalDate getDateExpirationApi() { return this.date_expiration_api; }

    @JsonProperty("departement")
    @org.kie.dmn.feel.lang.FEELProperty("departement")
    public String getDepartement() { return this.departement; }

    @JsonProperty("refugie_ou_protege_subsidiaire")
    @org.kie.dmn.feel.lang.FEELProperty("refugie_ou_protege_subsidiaire")
    public boolean getRefugie() { return this.refugie_ou_protege_subsidiaire; }

    @JsonProperty("risque_sur_l_emploi")
    @org.kie.dmn.feel.lang.FEELProperty("risque_sur_l_emploi")
    public boolean getRisqueEmploi() { return this.risque_sur_l_emploi; }

    public CustomerCase() {
    }

    public CustomerCase(LocalDate date_demande, 
                String departement,
                boolean refugie_ou_protege_subsidiaire,
                boolean risque_sur_l_emploi,
                LocalDate date_expiration_api) {
        this.date_demande = date_demande;
        this.departement = departement; // 78 or 92 for instance
        this.refugie_ou_protege_subsidiaire = refugie_ou_protege_subsidiaire;
        this.risque_sur_l_emploi = risque_sur_l_emploi;
        this.date_expiration_api = date_expiration_api;
    }
}