package trusted_services;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;

public class DateManagement {

	static LocalDate parse(String jmaaaa) {
		try {
			DateTimeFormatter formatter = DateTimeFormatter.ofPattern("d/M/yyyy");
			return LocalDate.parse(jmaaaa, formatter);
		} catch (DateTimeParseException e) {
			return LocalDate.now();
		}
	}

	public static long nbDeJoursDeDate1aDate2(String jmaaaa1, String jmaaaa2) {
		LocalDate date1 = parse(jmaaaa1);
		LocalDate date2 = parse(jmaaaa2);
		return ChronoUnit.DAYS.between(date1, date2);
	}

	public static boolean coincident(String jmaaaa1, String jmaaaa2) {
		LocalDate date1 = parse(jmaaaa1);
		LocalDate date2 = parse(jmaaaa2);
		return date1.equals(date2);
	}

	public static boolean estAvant(String jmaaaa1, String jmaaaa2) {
		LocalDate date1 = parse(jmaaaa1);
		LocalDate date2 = parse(jmaaaa2);
		return date1.isBefore(date2);
	}

	public static boolean estApres(String jmaaaa1, String jmaaaa2) {
		return estAvant(jmaaaa2, jmaaaa1);
	}
}
