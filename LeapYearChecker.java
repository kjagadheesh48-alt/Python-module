
public class LeapYearChecker {

    
    public static void is_leap_year(int year) {
        boolean is_leap_year = false;

        if (year % 4 == 0) {
            if (year % 100 == 0) {
                if (year % 400 == 0) {
                    is_leap_year = true;
                } else {
                    is_leap_year = false;
                }
            } else {
                is_leap_year = true;
            }
        } else {
            is_leap_year = false;
        }

        // Print the result
        if (is_leap_year) {
            System.out.println(year + " is a leap year.");
        } else {
            System.out.println(year + " is not a leap year.");
        }
    }

    public static void main(String[] args) {
        
        is_leap_year(2000); 
        is_leap_year(1900); 
        is_leap_year(2024); 
        is_leap_year(2023); 
    }
}
