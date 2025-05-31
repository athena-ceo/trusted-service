package trusted_services;

import java.util.ArrayList;
import java.util.List;

public class CaseHandlingDecision {

	Handling handling;

	String acknowledgement_to_requester;
	String response_template_id;

	String work_basket;
	Priority priority;
	List<String> notes = new ArrayList<>();

	public void increasePriorityLevel() {
		if (priority == Priority.VERY_LOW) {
			priority = Priority.LOW;
		} else if (priority == Priority.LOW) {
			priority = Priority.MEDIUM;
		} else if (priority == Priority.MEDIUM) {
			priority = Priority.HIGH;
		} else if (priority == Priority.HIGH) {
			priority = Priority.VERY_HIGH;
		}
	}

	public Handling getHandling() {
		return handling;
	}

	public void setHandling(Handling handling) {
		this.handling = handling;
	}

	public String getAcknowledgement_to_requester() {
		return acknowledgement_to_requester;
	}

	public void setAcknowledgement_to_requester(String acknowledgement_to_requester) {
		this.acknowledgement_to_requester = acknowledgement_to_requester;
	}

	public String getResponse_template_id() {
		return response_template_id;
	}

	public void setResponse_template_id(String response_template_id) {
		this.response_template_id = response_template_id;
	}

	public String getWork_basket() {
		return work_basket;
	}

	public void setWork_basket(String work_basket) {
		this.work_basket = work_basket;
	}

	public Priority getPriority() {
		return priority;
	}

	public void setPriority(Priority priority) {
		this.priority = priority;
	}

	public List<String> getNotes() {
		return notes;
	}

	public void setNotes(List<String> notes) {
		this.notes = notes;
	}

	public void addNote(String note) {
		this.notes.add(note);
	}
}
